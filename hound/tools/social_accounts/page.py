from PyQt6.QtWidgets import QLabel

from hound.ui.widgets.tool_page import ToolPage

TITLE = "Social Account Discovery"


class SocialAccountsPage(ToolPage):
    def __init__(self) -> None:
        super().__init__(TITLE)
        self.add_content(QLabel(f"{TITLE} goes here."))
