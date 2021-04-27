from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class AskGenerate(Popup):
    nodes_number: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab

    def generate(self):
        self.dismiss()

        try:
            nodes = int(self.nodes_number.text)
            if nodes < 1:
                raise ValueError('Nodes amount must be 1 or more')

        except ValueError as ve:
            ErrorPopup(f'Not correct nodes amount!\n{" ".join(ve.args)}').open()

        else:
            self.parent_tab.generate(nodes)
