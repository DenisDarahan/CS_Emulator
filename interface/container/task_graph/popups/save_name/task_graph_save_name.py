from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class TaskGraphSaveName(Popup):
    graph_name: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, callback, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab
        self.callback = callback

    def save(self):
        self.dismiss()

        name = self.graph_name.text
        if not name:
            ErrorPopup('Graph name cannot be empty!')
            return

        self.parent_tab.save(name, self.callback)
