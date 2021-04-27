from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class AskAddEdge(Popup):
    src_node_id: TextInput = ObjectProperty()
    dst_node_id: TextInput = ObjectProperty()
    edge_weight: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab

    def add_edge(self):
        self.dismiss()

        try:
            src_node_id = int(self.src_node_id.text) - 1
            dst_node_id = int(self.dst_node_id.text) - 1

            if not 0 <= src_node_id < len(self.parent_tab.nodes):
                raise ValueError(f'Src Node id must be between 1 and {len(self.parent_tab.nodes)}')

            if (not 0 <= dst_node_id < len(self.parent_tab.nodes)) or \
                    src_node_id == dst_node_id or (src_node_id, dst_node_id) in self.parent_tab.edges:
                raise ValueError(f'Dst Node id must be between 1 and {len(self.parent_tab.nodes)}')

            weight = int(self.edge_weight.text)
            if weight < 1:
                raise ValueError('Weight must be 1 or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct node id or weight!\n{" ".join(ve.args)}').open()

        else:
            return self.parent_tab.add_edge(weight, self.parent_tab.nodes[src_node_id],
                                            self.parent_tab.nodes[dst_node_id])
