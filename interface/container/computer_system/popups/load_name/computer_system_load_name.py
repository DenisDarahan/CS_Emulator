from os import path

from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup
from CS_Emulator.config import DUMP_PATH


class ComputerSystemLoadName(Popup):
    file_name: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab

    def load(self):
        self.dismiss()

        name = self.file_name.text
        if not name:
            ErrorPopup('File name cannot be empty!').open()
            return
        if not path.exists(f'{DUMP_PATH}/{self.parent_tab.graph.graph_type}_{name}.json'):
            ErrorPopup('File not found').open()
            return

        self.parent_tab.load(name)
