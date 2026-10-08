"""
Profile Sharing & Security Service.
Provides export and import of shareable Workspace Profiles with:
- Path generalization (replacing user-specific paths with %USERPROFILE% / %ProgramFiles%)
- Passcode-based authenticated encryption using standard library PBKDF2-HMAC-SHA256
- Integrity verification and validation
"""

from __future__ import annotations
import os
import json
import hmac
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from app.models.workspace import WorkspaceProfile
from app.configuration.validator import ConfigValidator
from app.logging.logger import get_logger

PBKDF2_ROUNDS = 100000
KEY_LEN = 32


class ProfileSharingService:
    """Handles secure export, path generalization, and encrypted import of workspace profiles."""

    def __init__(self):
        self.logger = get_logger()

    @staticmethod
    def generalize_paths(profile: WorkspaceProfile) -> WorkspaceProfile:
        """Replaces machine-specific username paths with generic environment variables."""
        profile_dict = profile.to_dict()
        user_profile = os.environ.get("USERPROFILE", "")
        username = os.environ.get("USERNAME", "")

        def _clean_str(val: str) -> str:
            if not isinstance(val, str) or not val:
                return val
            res = val
            if user_profile and user_profile in res:
                res = res.replace(user_profile, "%USERPROFILE%")
            elif username and f"\\{username}\\" in res:
                res = res.replace(f"\\{username}\\", "\\%USERNAME%\\")
            return res

        for app in profile_dict.get("apps", []):
            if "executable" in app:
                app["executable"] = _clean_str(app["executable"])
            if "arguments" in app:
                app["arguments"] = _clean_str(app["arguments"])

        return WorkspaceProfile.from_dict(profile_dict)

    @classmethod
    def _derive_keys(cls, passcode: str, salt: bytes) -> Tuple[bytes, bytes]:
        """Derives encryption key and HMAC verification key using PBKDF2-HMAC-SHA256."""
        derived = hashlib.pbkdf2_hmac("sha256", passcode.encode("utf-8"), salt, PBKDF2_ROUNDS, dklen=64)
        enc_key = derived[:32]
        mac_key = derived[32:]
        return enc_key, mac_key

    @classmethod
    def _keystream(cls, key: bytes, nonce: bytes, length: int) -> bytes:
        """Generates cryptographically secure keystream blocks using HMAC-SHA256 counter mode."""
        stream = bytearray()
        counter = 0
        while len(stream) < length:
            msg = nonce + counter.to_bytes(8, "big")
            block = hmac.new(key, msg, hashlib.sha256).digest()
            stream.extend(block)
            counter += 1
        return bytes(stream[:length])

    @classmethod
    def encrypt_payload(cls, data: bytes, passcode: str) -> Dict[str, Any]:
        """Encrypts data with passcode and returns authenticated envelope."""
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(16)
        enc_key, mac_key = cls._derive_keys(passcode, salt)

        keystream = cls._keystream(enc_key, nonce, len(data))
        ciphertext = bytes(a ^ b for a, b in zip(data, keystream))

        mac = hmac.new(mac_key, salt + nonce + ciphertext, hashlib.sha256).hexdigest()

        return {
            "format": "vdwm_encrypted",
            "version": 1,
            "kdf": "pbkdf2_hmac_sha256",
            "iterations": PBKDF2_ROUNDS,
            "salt": salt.hex(),
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
            "mac": mac
        }

    @classmethod
    def decrypt_payload(cls, envelope: Dict[str, Any], passcode: str) -> bytes:
        """Verifies integrity and decrypts authenticated envelope using passcode."""
        salt = bytes.fromhex(envelope["salt"])
        nonce = bytes.fromhex(envelope["nonce"])
        ciphertext = bytes.fromhex(envelope["ciphertext"])
        expected_mac = envelope["mac"]

        enc_key, mac_key = cls._derive_keys(passcode, salt)

        calc_mac = hmac.new(mac_key, salt + nonce + ciphertext, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc_mac, expected_mac):
            raise ValueError("Incorrect passcode or corrupted profile bundle.")

        keystream = cls._keystream(enc_key, nonce, len(ciphertext))
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, keystream))
        return plaintext

    def export_profile(
        self,
        profile: WorkspaceProfile,
        target_path: Path,
        passcode: Optional[str] = None,
        sanitize_paths: bool = True
    ) -> Path:
        """Exports profile to file, optionally sanitized and passcode-encrypted."""
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        export_prof = self.generalize_paths(profile) if sanitize_paths else profile
        payload_dict = {
            "schema_version": 1,
            "profile": export_prof.to_dict()
        }
        json_bytes = json.dumps(payload_dict, indent=2, ensure_ascii=False).encode("utf-8")

        if passcode:
            envelope = self.encrypt_payload(json_bytes, passcode)
            target_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
            self.logger.info(f"Exported encrypted profile to {target_path}")
        else:
            target_path.write_bytes(json_bytes)
            self.logger.info(f"Exported plain profile to {target_path}")

        return target_path

    def import_profile(self, source_path: Path, passcode: Optional[str] = None) -> WorkspaceProfile:
        """Imports and validates a profile from file, prompting for decryption if encrypted."""
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Profile bundle not found: {source_path}")

        raw_text = source_path.read_text(encoding="utf-8")
        parsed = json.loads(raw_text)

        if parsed.get("format") == "vdwm_encrypted":
            if not passcode:
                raise ValueError("This profile bundle is passcode-protected. A passcode is required.")
            raw_bytes = self.decrypt_payload(parsed, passcode)
            parsed = json.loads(raw_bytes.decode("utf-8"))

        profile_data = parsed.get("profile", parsed)
        profile = WorkspaceProfile.from_dict(profile_data)

        # Validate imported profile
        errors, warnings = ConfigValidator.validate_profile(profile)
        if errors:
            raise ValueError(f"Imported profile validation failed: {'; '.join(errors)}")

        self.logger.info(f"Successfully imported profile '{profile.name}' from {source_path}")
        return profile
