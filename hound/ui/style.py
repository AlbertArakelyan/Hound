"""Shared look of the app: colours, radii, and the stylesheets built from them.

Greys and accents are given as alpha over whatever the theme background is, so the
same values read correctly in a light theme and a dark one. Nothing here hardcodes a
background colour.
"""

ACCENT = "124, 92, 255"
FOUND = "64, 174, 96"
UNKNOWN = "201, 138, 27"
MUTED = "127, 127, 127"

RADIUS = "8px"
CARD_RADIUS = "12px"


def muted(alpha: float = 1.0) -> str:
    return f"rgba({MUTED}, {alpha})"


def accent(alpha: float = 1.0) -> str:
    return f"rgba({ACCENT}, {alpha})"


def panel_style(name: str) -> str:
    return f"""
    #{name} {{
        background-color: rgba({MUTED}, 0.05);
        border: 1px solid rgba({MUTED}, 0.25);
        border-radius: {RADIUS};
    }}
    """


def card_style(name: str) -> str:
    return f"""
    #{name} {{
        background-color: rgba({MUTED}, 0.07);
        border: 1px solid rgba({MUTED}, 0.28);
        border-radius: {CARD_RADIUS};
    }}
    #{name}:hover {{
        background-color: rgba({ACCENT}, 0.10);
        border: 1px solid rgba({ACCENT}, 0.70);
    }}
    """


def input_style() -> str:
    return f"""
    QLineEdit, QSpinBox {{
        background-color: rgba({MUTED}, 0.08);
        border: 1px solid rgba({MUTED}, 0.30);
        border-radius: {RADIUS};
        padding: 6px 10px;
        selection-background-color: rgba({ACCENT}, 0.45);
    }}
    QLineEdit:focus, QSpinBox:focus {{
        border: 1px solid rgba({ACCENT}, 0.80);
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: transparent;
        border: none;
        width: 16px;
    }}
    """


def primary_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: rgba({ACCENT}, 0.85);
        color: white;
        border: none;
        border-radius: {RADIUS};
        padding: 7px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: rgba({ACCENT}, 1.0); }}
    QPushButton:disabled {{
        background-color: rgba({MUTED}, 0.20);
        color: rgba({MUTED}, 0.9);
    }}
    """


def quiet_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: transparent;
        border: 1px solid rgba({MUTED}, 0.35);
        border-radius: {RADIUS};
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        border: 1px solid rgba({ACCENT}, 0.70);
        color: rgba({ACCENT}, 1.0);
    }}
    QPushButton:disabled {{
        border: 1px solid rgba({MUTED}, 0.18);
        color: rgba({MUTED}, 0.6);
    }}
    """


def link(url: str, text: str | None = None) -> str:
    """An anchor that stays readable on both themes.

    Qt's default link blue is close to unreadable on a dark background, and QLabel
    ignores a stylesheet colour for anchors, so the colour goes inline.
    """
    return (f'<a href="{url}" style="color: rgb({ACCENT}); '
            f'text-decoration: none;">{text or url}</a>')
