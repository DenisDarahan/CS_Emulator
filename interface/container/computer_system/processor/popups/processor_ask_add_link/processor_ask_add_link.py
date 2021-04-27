from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class ProcessorAskAddLink(Popup):
    dst_proc_id: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, src_proc, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab
        self.src_proc = src_proc

    def add_link(self):
        self.dismiss()

        try:
            dst_proc_id = int(self.dst_proc_id.text) - 1
            if (not 0 <= dst_proc_id < len(self.parent_tab.processors)) or \
                    self.src_proc.proc_id == dst_proc_id or \
                    (self.src_proc.proc_id, dst_proc_id) in self.parent_tab.processors:
                raise ValueError(f'Dst Proc id must be between 1 and {len(self.parent_tab.processors)}')

        except ValueError as ve:
            ErrorPopup(f'Not correct processor id!\n{" ".join(ve.args)}').open()

        else:
            return self.parent_tab.add_link(self.src_proc, self.parent_tab.processors[dst_proc_id])
