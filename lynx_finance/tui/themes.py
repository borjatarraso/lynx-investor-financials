"""Custom Textual themes for the lynx-finance TUI application."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.theme import Theme

if TYPE_CHECKING:
    from textual.app import App

LYNX_DARK = Theme(
    name="finance-dark",
    primary="#89b4fa",
    secondary="#a6adc8",
    accent="#f9e2af",
    warning="#fab387",
    error="#f38ba8",
    success="#a6e3a1",
    foreground="#cdd6f4",
    background="#1e1e2e",
    surface="#313244",
    panel="#45475a",
    dark=True,
)

HACKER = Theme(
    name="hacker",
    primary="#00ff41",
    secondary="#00cc33",
    accent="#39ff14",
    warning="#ffff00",
    error="#ff0000",
    success="#00ff41",
    foreground="#00ff41",
    background="#0a0a0a",
    surface="#0d1a0d",
    panel="#142814",
    dark=True,
)

DRACULA = Theme(
    name="dracula",
    primary="#bd93f9",
    secondary="#f8f8f2",
    accent="#ff79c6",
    warning="#f1fa8c",
    error="#ff5555",
    success="#50fa7b",
    foreground="#f8f8f2",
    background="#282a36",
    surface="#44475a",
    panel="#6272a4",
    dark=True,
)

SOLARIZED = Theme(
    name="solarized",
    primary="#268bd2",
    secondary="#93a1a1",
    accent="#b58900",
    warning="#cb4b16",
    error="#dc322f",
    success="#859900",
    foreground="#839496",
    background="#002b36",
    surface="#073642",
    panel="#586e75",
    dark=True,
)

LYNX_LIGHT = Theme(
    name="finance-light",
    primary="#1e66f5",
    secondary="#6c6f85",
    accent="#df8e1d",
    warning="#fe640b",
    error="#d20f39",
    success="#40a02b",
    foreground="#4c4f69",
    background="#eff1f5",
    surface="#e6e9ef",
    panel="#ccd0da",
    dark=False,
)

# Cyberpunk-style theme with neon accents on a near-black base —
# electric cyan / hot magenta / lime green, leaning into the "cybr" aesthetic.
CYBRDOTS = Theme(
    name="cybrdots",
    primary="#00f0ff",       # electric cyan
    secondary="#ff2bd6",     # hot magenta / neon pink
    accent="#c6ff00",        # lime green
    warning="#ffb000",       # amber
    error="#ff2d5a",         # neon red
    success="#39ff14",       # neon green
    foreground="#e0f7ff",    # pale cyan text
    background="#0a0014",    # deep purple-black
    surface="#140028",       # midnight violet
    panel="#1f0a3c",         # dark indigo panel
    dark=True,
)

CUSTOM_THEMES: list[Theme] = [LYNX_DARK, HACKER, DRACULA, SOLARIZED, CYBRDOTS, LYNX_LIGHT]

THEME_NAMES: list[str] = [
    "finance-dark", "hacker", "dracula", "solarized", "cybrdots", "finance-light",
    "textual-dark", "textual-light",
]

def register_all_themes(app: App) -> None:
    for theme in CUSTOM_THEMES:
        app.register_theme(theme)
