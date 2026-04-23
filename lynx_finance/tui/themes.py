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



HOUSE_THEMES: List[Theme] = [LYNX_DARK, LYNX_LIGHT]

CUSTOM_THEMES: List[Theme] = HOUSE_THEMES + SUITE_THEMES

THEME_NAMES: List[str] = (
    ["finance-dark", "finance-light", "cybrdots"] + SUITE_THEME_NAMES + ["textual-dark", "textual-light"]
)


def register_all_themes(app: "App") -> None:
    """Register every house + Suite theme on *app*."""
    for theme in HOUSE_THEMES:
        app.register_theme(theme)
    register_suite_themes(app)
