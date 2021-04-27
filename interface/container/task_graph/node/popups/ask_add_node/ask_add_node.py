from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class AskAddNode(Popup):
    node_weight: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab

    def add_node(self):
        self.dismiss()

        try:
            weight = int(self.node_weight.text)
            if weight < 1:
                raise ValueError('Weight must be 1 or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct node weight!\n{" ".join(ve.args)}').open()

        else:
            self.parent_tab.add_node(weight)
