"""
Modern styling and themes for Tkinter / ttk desktop UI.
Supports clean Windows 11 style palette in Light and Dark themes.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class ThemeManager:
    """Manages color palettes and TTK style configurations."""

    LIGHT_THEME: Dict[str, str] = {
        "bg": "#f3f3f3",
        "surface": "#ffffff",
        "surface_secondary": "#f9f9f9",
        "border": "#e0e0e0",
        "border_focus": "#0067c0",
        "fg": "#1a1a1a",
        "fg_muted": "#5f5f5f",
        "primary": "#0067c0",
        "primary_hover": "#005a9e",
        "primary_fg": "#ffffff",
        "success": "#107c41",
        "warning": "#b25900",
        "error": "#d13438",
        "active_card_bg": "#edf5fd",
        "active_card_border": "#0067c0",
        "card_bg": "#ffffff",
        "log_bg": "#1e1e1e",
        "log_fg": "#d4d4d4"
    }

    DARK_THEME: Dict[str, str] = {
        "bg": "#202020",
        "surface": "#2d2d2d",
        "surface_secondary": "#333333",
        "border": "#404040",
        "border_focus": "#4cc2ff",
        "fg": "#f0f0f0",
        "fg_muted": "#a0a0a0",
        "primary": "#4cc2ff",
        "primary_hover": "#3a9fd9",
        "primary_fg": "#000000",
        "success": "#6ccb5f",
        "warning": "#fce100",
        "error": "#ff6a6a",
        "active_card_bg": "#1c3245",
        "active_card_border": "#4cc2ff",
        "card_bg": "#2b2b2b",
        "log_bg": "#181818",
        "log_fg": "#dcdcdc"
    }

    @classmethod
    def get_palette(cls, theme_preference: str = "System") -> Dict[str, str]:
        """Resolves palette based on preference (System defaults to Light or detects Windows dark mode)."""
        pref = theme_preference.lower()
        if pref == "dark":
            return cls.DARK_THEME
        elif pref == "light":
            return cls.LIGHT_THEME

        # Detect Windows dark mode from registry
        import winreg
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return cls.LIGHT_THEME if val == 1 else cls.DARK_THEME
        except Exception:
            return cls.LIGHT_THEME

    @classmethod
    def apply_theme(cls, root: tk.Tk, theme_preference: str = "System") -> Dict[str, str]:
        """Configures ttk styles for the active theme."""
        palette = cls.get_palette(theme_preference)
        style = ttk.Style(root)

        root.configure(bg=palette["bg"])

        # Base style configs
        style.theme_use("clam")

        style.configure(".",
            background=palette["bg"],
            foreground=palette["fg"],
            font=("Segoe UI", 9)
        )

        style.configure("TFrame", background=palette["bg"])
        style.configure("Surface.TFrame", background=palette["surface"])
        style.configure("Card.TFrame", background=palette["card_bg"], relief="flat")

        style.configure("TLabel",
            background=palette["bg"],
            foreground=palette["fg"],
            font=("Segoe UI", 9)
        )
        style.configure("Muted.TLabel", foreground=palette["fg_muted"], font=("Segoe UI", 8))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Surface.TLabel", background=palette["surface"])

        # Status badge labels
        style.configure("Success.TLabel", foreground=palette["success"], font=("Segoe UI", 9, "bold"))
        style.configure("Warning.TLabel", foreground=palette["warning"], font=("Segoe UI", 9, "bold"))
        style.configure("Error.TLabel", foreground=palette["error"], font=("Segoe UI", 9, "bold"))

        # Buttons
        style.configure("TButton",
            padding=(10, 5),
            relief="flat",
            borderwidth=1,
            focuscolor=palette["border_focus"],
            font=("Segoe UI", 9)
        )

        style.configure("Primary.TButton",
            background=palette["primary"],
            foreground=palette["primary_fg"],
            padding=(12, 6),
            font=("Segoe UI", 9, "bold")
        )
        style.map("Primary.TButton",
            background=[("active", palette["primary_hover"])],
            relief=[("pressed", "sunken")]
        )

        style.configure("Danger.TButton",
            background=palette["error"],
            foreground="#ffffff",
            padding=(10, 5),
            font=("Segoe UI", 9, "bold")
        )

        style.configure("TLabelframe", background=palette["surface"], foreground=palette["fg"])
        style.configure("TLabelframe.Label", background=palette["surface"], foreground=palette["primary"], font=("Segoe UI", 9, "bold"))

        style.configure("TNotebook", background=palette["bg"], tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Segoe UI", 9))

        return palette
