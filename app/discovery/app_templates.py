"""
Templates for common Windows applications to assist discovery and configuration.
Templates provide default paths, candidate process names, and window policies.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class AppTemplate:
    """Pre-configured definition template for an application."""
    id: str
    name: str
    default_desktop: int
    candidate_paths: List[str]
    process_names: List[str]
    window_policy: str = "main"
    default_arguments: str = ""
    description: str = ""


APPLICATION_TEMPLATES: List[AppTemplate] = [
    AppTemplate(
        id="brave",
        name="Brave Browser",
        default_desktop=1,
        candidate_paths=[
            r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ],
        process_names=["brave.exe"],
        window_policy="main",
        description="Privacy-focused web browser"
    ),
    AppTemplate(
        id="chrome",
        name="Google Chrome",
        default_desktop=1,
        candidate_paths=[
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
        ],
        process_names=["chrome.exe"],
        window_policy="main",
        description="Google Chrome web browser"
    ),
    AppTemplate(
        id="edge",
        name="Microsoft Edge",
        default_desktop=1,
        candidate_paths=[
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
        ],
        process_names=["msedge.exe"],
        window_policy="main",
        description="Microsoft Edge browser"
    ),
    AppTemplate(
        id="firefox",
        name="Mozilla Firefox",
        default_desktop=1,
        candidate_paths=[
            r"%ProgramFiles%\Mozilla Firefox\firefox.exe",
            r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
        ],
        process_names=["firefox.exe"],
        window_policy="main",
        description="Mozilla Firefox browser"
    ),
    AppTemplate(
        id="antigravity",
        name="Google Antigravity",
        default_desktop=2,
        candidate_paths=[
            r"%LocalAppData%\Programs\Google Antigravity\Google Antigravity.exe",
            r"%LocalAppData%\Google\Antigravity\antigravity.exe",
            r"%ProgramFiles%\Google\Antigravity\antigravity.exe"
        ],
        process_names=["Google Antigravity.exe", "antigravity.exe", "agy.exe"],
        window_policy="main",
        description="Google Antigravity Advanced Agentic IDE"
    ),
    AppTemplate(
        id="vscode",
        name="Visual Studio Code",
        default_desktop=2,
        candidate_paths=[
            r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe",
            r"%ProgramFiles%\Microsoft VS Code\Code.exe"
        ],
        process_names=["Code.exe"],
        window_policy="all",
        description="Code editor by Microsoft"
    ),
    AppTemplate(
        id="visualstudio",
        name="Visual Studio",
        default_desktop=2,
        candidate_paths=[
            r"%ProgramFiles%\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
            r"%ProgramFiles%\Microsoft Visual Studio\2022\Professional\Common7\IDE\devenv.exe",
            r"%ProgramFiles%\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe"
        ],
        process_names=["devenv.exe"],
        window_policy="main",
        description="Microsoft Visual Studio IDE"
    ),
    AppTemplate(
        id="gitbash",
        name="Git Bash",
        default_desktop=2,
        candidate_paths=[
            r"%ProgramFiles%\Git\git-bash.exe",
            r"%LocalAppData%\Programs\Git\git-bash.exe"
        ],
        process_names=["git-bash.exe", "mintty.exe"],
        window_policy="all",
        description="Git Bash terminal environment"
    ),
    AppTemplate(
        id="terminal",
        name="Windows Terminal",
        default_desktop=2,
        candidate_paths=[
            r"%LocalAppData%\Microsoft\WindowsApps\wt.exe"
        ],
        process_names=["WindowsTerminal.exe", "wt.exe"],
        window_policy="all",
        description="Modern Windows Terminal"
    ),
    AppTemplate(
        id="ssms",
        name="SQL Server Management Studio",
        default_desktop=3,
        candidate_paths=[
            r"%ProgramFiles(x86)%\Microsoft SQL Server Management Studio 20\Common7\IDE\Ssms.exe",
            r"%ProgramFiles(x86)%\Microsoft SQL Server Management Studio 19\Common7\IDE\Ssms.exe",
            r"%ProgramFiles(x86)%\Microsoft SQL Server Management Studio 18\Common7\IDE\Ssms.exe",
            r"%ProgramFiles%\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe"
        ],
        process_names=["Ssms.exe"],
        window_policy="main",
        description="Database management tool for SQL Server"
    ),
    AppTemplate(
        id="postman",
        name="Postman",
        default_desktop=4,
        candidate_paths=[
            r"%LocalAppData%\Postman\Postman.exe",
            r"%LocalAppData%\Postman\app-*\Postman.exe"
        ],
        process_names=["Postman.exe"],
        window_policy="main",
        description="API platform for building and using APIs"
    ),
    AppTemplate(
        id="docker",
        name="Docker Desktop",
        default_desktop=4,
        candidate_paths=[
            r"%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
        ],
        process_names=["Docker Desktop.exe"],
        window_policy="main",
        description="Docker container environment"
    ),
    AppTemplate(
        id="explorer",
        name="File Explorer",
        default_desktop=1,
        candidate_paths=[
            r"%SystemRoot%\explorer.exe"
        ],
        process_names=["explorer.exe"],
        window_policy="all",
        description="Windows File Explorer"
    )
]


def get_template_by_id(template_id: str) -> Optional[AppTemplate]:
    """Finds a template matching given ID."""
    for t in APPLICATION_TEMPLATES:
        if t.id.lower() == template_id.lower():
            return t
    return None
