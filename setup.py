"""
Setup script for Virtual Desktop Workspace Manager.
"""

from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="virtual-desktop-workspace-manager",
    version="1.0.0",
    description="Production Windows 10/11 Virtual Desktop Workspace Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Production Engineering Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pyvda>=0.6.0",
        "pywin32>=306",
        "psutil>=5.9.0",
        "comtypes>=1.4.0",
        "pystray>=0.19.5",
        "Pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pyinstaller>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "vdwm=app.main:main",
            "vdwm-configure=app.main:main",
            "vdwm-run=run_workspace:main",
        ],
        "gui_scripts": [
            "vdwm-gui=app.main:main",
        ],
    },
    classifiers=[
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
)
