import tgmenu.button_types
from tgmenu.directory import Directory as Di


class Button:
    def __init__(self, text: str,
                 btn_type: int = tgmenu.button_types.btn_default,
                 target_directory: Di = None):
        self.text = text
        self.btn_type = btn_type
        self.directory = None
        self.target_directory = target_directory
