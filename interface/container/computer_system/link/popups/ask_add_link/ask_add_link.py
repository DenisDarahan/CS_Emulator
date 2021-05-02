from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from interface.popups import ErrorPopup


class AskAddLink(Popup):
    src_proc_id: TextInput = ObjectProperty()
    dst_proc_id: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab

    def add_link(self):
        self.dismiss()

        try:
            src_proc_id = int(self.src_proc_id.text) - 1
            dst_proc_id = int(self.dst_proc_id.text) - 1

            if not 0 <= src_proc_id < len(self.parent_tab.processors):
                raise ValueError(f'Src Processor id must be between 1 and {len(self.parent_tab.processors)}')

            if (not 0 <= dst_proc_id < len(self.parent_tab.processors)) or \
                    src_proc_id == dst_proc_id or (src_proc_id, dst_proc_id) in self.parent_tab.links:
                raise ValueError(f'Dst Processor id must be between 1 and {len(self.parent_tab.processors)}')

        except ValueError as ve:
            ErrorPopup(f'Not correct processor id!\n{" ".join(ve.args)}').open()

        else:
            return self.parent_tab.add_link(self.parent_tab.processors[src_proc_id],
                                            self.parent_tab.processors[dst_proc_id])
