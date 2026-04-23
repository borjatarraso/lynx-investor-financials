"""Custom Textual themes for the lynx-finance TUI application.

Ships a small set of sector-flavored "house" themes plus the full
Suite-wide gallery (Catppuccin, Dracula, Tokyo Night, Nord, Gruvbox,
Kanagawa, Matrix, Synthwave '84, and more) — see
:mod:`lynx_investor_core.themes` for the full list.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from textual.theme import Theme

from lynx_investor_core.themes import (
    SUITE_THEMES,
    SUITE_THEME_NAMES,
    register_suite_themes,
)

if TYPE_CHECKING:
    from textual.app import App


# Sector-flavored "house" themes (kept from prior versions).

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

HOUSE_THEMES: List[Theme] = [LYNX_DARK, LYNX_LIGHT, CYBRDOTS]

CUSTOM_THEMES: List[Theme] = HOUSE_THEMES + SUITE_THEMES

THEME_NAMES: List[str] = (
    ["finance-dark", "finance-light", "cybrdots"] + SUITE_THEME_NAMES + ["textual-dark", "textual-light"]
)


def register_all_themes(app: "App") -> None:
    """Register every house + Suite theme on *app*."""
    for theme in HOUSE_THEMES:
        app.register_theme(theme)
    register_suite_themes(app)
