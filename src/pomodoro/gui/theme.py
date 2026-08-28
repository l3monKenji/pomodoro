"""Central design tokens and the QSS stylesheet built from them.

Colors are chosen to support focus rather than fight for attention: blue
for the analytical, calm Focus phase; green for the restorative Break
phase; quiet neutrals everywhere else; red/amber reserved for the one
destructive action in the app (resetting history).
"""

from __future__ import annotations

from dataclasses import dataclass

FONT_FAMILY = '"Helvetica Neue", Helvetica, Arial, sans-serif'
FONT_FAMILY_MONO = "Menlo, Monaco, Consolas, monospace"

SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 20
SPACE_XL = 32

RADIUS_SM = 8
RADIUS_MD = 14
RADIUS_LG = 22

WINDOW_SIZE = (960, 640)


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    name: str
    bg_window: str
    bg_elevated: str
    bg_elevated_alt: str
    bg_pressed: str
    border: str
    border_strong: str
    text_primary: str
    text_secondary: str
    text_muted: str
    focus: str
    focus_hover: str
    focus_pressed: str
    focus_soft: str
    break_: str
    break_hover: str
    break_pressed: str
    break_soft: str
    warn: str
    danger: str
    danger_hover: str


DARK = ThemeTokens(
    name="dark",
    bg_window="#0f1620",
    bg_elevated="#171f2a",
    bg_elevated_alt="#1d2733",
    bg_pressed="#141b25",
    border="#28323f",
    border_strong="#3a4655",
    text_primary="#edf1f6",
    text_secondary="#9aa8b8",
    text_muted="#697687",
    focus="#4f8cff",
    focus_hover="#6b9fff",
    focus_pressed="#3d74e0",
    focus_soft="#1e2c42",
    break_="#33d6a0",
    break_hover="#52e0b0",
    break_pressed="#26b686",
    break_soft="#173428",
    warn="#e0a33e",
    danger="#e0655d",
    danger_hover="#e9807a",
)

LIGHT = ThemeTokens(
    name="light",
    bg_window="#f3f6f9",
    bg_elevated="#ffffff",
    bg_elevated_alt="#eef2f6",
    bg_pressed="#e4e9ee",
    border="#dde3ea",
    border_strong="#c7d0da",
    text_primary="#1b2530",
    text_secondary="#57626e",
    text_muted="#8a95a1",
    focus="#2f6fed",
    focus_hover="#1f5ad9",
    focus_pressed="#1a4bb8",
    focus_soft="#dce6fb",
    break_="#12a97a",
    break_hover="#0f8f68",
    break_pressed="#0c7657",
    break_soft="#d8f3e8",
    warn="#b5790a",
    danger="#c94a43",
    danger_hover="#b53f38",
)

def themes_by_name() -> dict[str, ThemeTokens]:
    return {"dark": DARK, "light": LIGHT}


def build_stylesheet(t: ThemeTokens) -> str:
    return f"""
    * {{
        font-family: {FONT_FAMILY};
        color: {t.text_primary};
        outline: none;
    }}

    QMainWindow, QWidget#rootView {{
        background: {t.bg_window};
    }}

    QWidget {{
        background: transparent;
    }}

    QLabel#appTitle {{
        font-size: 15px;
        font-weight: 600;
        color: {t.text_primary};
        letter-spacing: 0.5px;
    }}

    QLabel#appSubtitle {{
        font-size: 11px;
        color: {t.text_muted};
    }}

    /* --- Tabs -------------------------------------------------------- */
    QTabWidget::pane {{
        border: none;
        background: transparent;
        top: 0px;
    }}

    QTabBar {{
        background: transparent;
    }}

    QTabBar::tab {{
        background: transparent;
        color: {t.text_secondary};
        padding: 10px 18px;
        margin-right: 4px;
        border-bottom: 2px solid transparent;
        font-size: 13px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        color: {t.text_primary};
        border-bottom: 2px solid {t.focus};
    }}

    QTabBar::tab:hover:!selected {{
        color: {t.text_primary};
    }}

    /* --- Cards --------------------------------------------------------*/
    QFrame#card {{
        background: {t.bg_elevated};
        border: 1px solid {t.border};
        border-radius: {RADIUS_MD}px;
    }}

    QLabel#cardTitle {{
        font-size: 13px;
        font-weight: 700;
        color: {t.text_secondary};
        letter-spacing: 0.6px;
    }}

    /* --- Countdown / phase labels ------------------------------------*/
    QLabel#countdownLabel {{
        font-family: {FONT_FAMILY_MONO};
        font-size: 64px;
        font-weight: 600;
        color: {t.text_primary};
    }}

    QLabel#phaseLabel {{
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }}

    QLabel#roundLabel {{
        font-size: 12px;
        color: {t.text_secondary};
        font-weight: 500;
    }}

    QLabel#hintLabel {{
        font-size: 11px;
        color: {t.text_muted};
    }}

    QLabel#statValue {{
        font-size: 26px;
        font-weight: 700;
        color: {t.text_primary};
    }}

    QLabel#statLabel {{
        font-size: 11px;
        color: {t.text_muted};
        font-weight: 600;
        letter-spacing: 0.4px;
    }}

    /* --- Buttons --------------------------------------------------- */
    QPushButton {{
        border-radius: {RADIUS_SM}px;
        padding: 10px 22px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid transparent;
    }}

    QPushButton#primaryButton {{
        background: {t.focus};
        color: #ffffff;
    }}
    QPushButton#primaryButton:hover {{ background: {t.focus_hover}; }}
    QPushButton#primaryButton:pressed {{ background: {t.focus_pressed}; }}
    QPushButton#primaryButton:disabled {{ background: {t.bg_elevated_alt}; color: {t.text_muted}; }}

    QPushButton#breakButton {{
        background: {t.break_};
        color: #04140e;
    }}
    QPushButton#breakButton:hover {{ background: {t.break_hover}; }}
    QPushButton#breakButton:pressed {{ background: {t.break_pressed}; }}

    QPushButton#secondaryButton {{
        background: {t.bg_elevated_alt};
        border: 1px solid {t.border_strong};
        color: {t.text_primary};
    }}
    QPushButton#secondaryButton:hover {{ background: {t.bg_pressed}; border-color: {t.text_muted}; }}
    QPushButton#secondaryButton:pressed {{ background: {t.bg_pressed}; }}
    QPushButton#secondaryButton:disabled {{ color: {t.text_muted}; }}

    QPushButton#ghostButton {{
        background: transparent;
        color: {t.text_secondary};
        padding: 6px 10px;
        font-size: 12px;
    }}
    QPushButton#ghostButton:hover {{ color: {t.text_primary}; }}

    QPushButton#dangerButton {{
        background: transparent;
        border: 1px solid {t.danger};
        color: {t.danger};
    }}
    QPushButton#dangerButton:hover {{ background: {t.danger}; color: #ffffff; }}
    QPushButton#dangerButton:pressed {{ background: {t.danger_hover}; color: #ffffff; }}

    /* --- Inputs ------------------------------------------------------ */
    QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {{
        background: {t.bg_elevated_alt};
        border: 1px solid {t.border};
        border-radius: {RADIUS_SM}px;
        padding: 6px 10px;
        font-size: 13px;
        min-height: 22px;
    }}
    QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {t.focus};
    }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        width: 16px;
        border: none;
        background: transparent;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}
    QComboBox QAbstractItemView {{
        background: {t.bg_elevated};
        border: 1px solid {t.border};
        selection-background-color: {t.focus_soft};
        selection-color: {t.text_primary};
        outline: none;
    }}

    QCheckBox {{
        font-size: 13px;
        color: {t.text_primary};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1px solid {t.border_strong};
        background: {t.bg_elevated_alt};
    }}
    QCheckBox::indicator:checked {{
        background: {t.focus};
        border-color: {t.focus};
    }}

    QLabel {{
        font-size: 13px;
    }}

    /* --- Scroll areas -------------------------------------------------*/
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {t.border_strong};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QMessageBox {{
        background: {t.bg_elevated};
    }}
    """
