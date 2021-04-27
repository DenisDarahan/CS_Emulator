from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem


class ComputerSystemSave(Popup):

    def __init__(self, parent_tab: TabbedPanelItem, callback, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab
        self.callback = callback

    def save(self):
        self.dismiss()
        self.parent_tab.ask_save_name(self.callback)

    def skip(self):
        self.dismiss()
        self.callback()
