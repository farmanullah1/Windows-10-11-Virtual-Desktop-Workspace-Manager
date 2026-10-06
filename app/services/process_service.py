"""
Production process service providing safe execution, running process detection,
and process tree inspection without shell injection risks.
"""

from __future__ import annotations
import os
import shlex
import subprocess
from typing import List, Optional
import psutil

from app.providers.base import IProcessProvider, IApplicationLauncher, ProcessInfo
from app.logging.logger import get_logger


class ProcessService(IProcessProvider, IApplicationLauncher):
    """Handles process queries and safe execution."""

    def __init__(self):
        self.logger = get_logger()

    # -------------------------------------------------------------
    # IProcessProvider Implementation
    # -------------------------------------------------------------

    def is_process_running(self, executable_name_or_path: str) -> bool:
        if not executable_name_or_path:
            return False
        target = os.path.basename(executable_name_or_path).lower()
        full_target = os.path.normpath(executable_name_or_path).lower()

        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                p_name = (proc.info.get('name') or '').lower()
                p_exe = (proc.info.get('exe') or '').lower()
                if p_name == target:
                    return True
                if p_exe and os.path.normpath(p_exe) == full_target:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def get_running_processes_matching(self, names_or_paths: List[str]) -> List[ProcessInfo]:
        targets = {os.path.basename(p).lower() for p in names_or_paths if p}
        full_targets = {os.path.normpath(p).lower() for p in names_or_paths if p}
        results: List[ProcessInfo] = []

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                p_name = (proc.info.get('name') or '').lower()
                p_exe = (proc.info.get('exe') or '').lower()

                match = False
                if p_name in targets:
                    match = True
                elif p_exe and os.path.normpath(p_exe) in full_targets:
                    match = True

                if match:
                    results.append(ProcessInfo(
                        pid=proc.info['pid'],
                        name=proc.info.get('name') or '',
                        executable_path=proc.info.get('exe') or '',
                        cmdline=proc.info.get('cmdline') or []
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return results

    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        try:
            proc = psutil.Process(pid)
            return ProcessInfo(
                pid=pid,
                name=proc.name(),
                executable_path=proc.exe(),
                cmdline=proc.cmdline()
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    def get_all_running_processes(self) -> List[ProcessInfo]:
        results: List[ProcessInfo] = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                exe = proc.info.get('exe') or ''
                if not exe:
                    continue
                results.append(ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info.get('name') or '',
                    executable_path=exe,
                    cmdline=proc.info.get('cmdline') or []
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return results

    # -------------------------------------------------------------
    # IApplicationLauncher Implementation
    # -------------------------------------------------------------

    def launch(self, executable: str, arguments: str = "", working_dir: Optional[str] = None) -> int:
        """
        Spawns application process safely.
        Never uses shell=True to eliminate command injection.
        """
        expanded_exe = os.path.expandvars(executable)
        if not os.path.exists(expanded_exe):
            raise FileNotFoundError(f"Executable does not exist: {expanded_exe}")

        cmd = [expanded_exe]
        if arguments:
            # Safely split arguments
            try:
                extra_args = shlex.split(arguments, posix=False)
                cmd.extend(extra_args)
            except Exception:
                cmd.append(arguments)

        cwd = working_dir if (working_dir and os.path.isdir(working_dir)) else os.path.dirname(expanded_exe)
        if not cwd or not os.path.isdir(cwd):
            cwd = None

        self.logger.info(f"Launching process: {expanded_exe} with args: '{arguments}'")

        try:
            # DETACHED_PROCESS to allow the launched app to run independently
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                creationflags=creationflags,
                close_fds=True
            )
            self.logger.success(f"Started process '{os.path.basename(expanded_exe)}' (PID {proc.pid})")
            return proc.pid
        except Exception as ex:
            self.logger.error(f"Failed to launch '{expanded_exe}': {ex}")
            raise RuntimeError(f"Failed to launch '{expanded_exe}': {ex}") from ex
