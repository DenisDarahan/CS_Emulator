from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem


class AskQueue(Popup):

    def __init__(self, parent_tab: TabbedPanelItem, callback, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab
        self.callback = callback

    def map_queue(self, queue_type: str):
        if queue_type == '2':
            return self.parent_tab.tg_tab.graph.lab_02

        elif queue_type == '4':
            return self.parent_tab.tg_tab.graph.lab_03

        elif queue_type == '8':
            return self.parent_tab.tg_tab.graph.lab_04

        raise ValueError(f'Unknown queue type: {queue_type}')

    def set_queue(self, queue_type: str):
        self.dismiss()
        self.callback(self.map_queue(queue_type))
