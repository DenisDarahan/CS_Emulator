from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from interface.popups import ErrorPopup


class AskGenerate(Popup):
    nodes_min_weight: TextInput = ObjectProperty()
    nodes_max_weight: TextInput = ObjectProperty()
    nodes_number: TextInput = ObjectProperty()
    graph_correlation: TextInput = ObjectProperty()
    edges_min_weight: TextInput = ObjectProperty()
    edges_max_weight: TextInput = ObjectProperty()

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        super().__init__(**kwargs)
        self.parent_tab = parent_tab

    def generate(self):
        self.dismiss()

        try:
            n_min_weight = int(self.nodes_min_weight.text)
            if n_min_weight < 1:
                raise ValueError('Nodes min weight must be 1 or greater')

            n_max_weight = int(self.nodes_max_weight.text)
            if n_max_weight < n_min_weight:
                raise ValueError(f'Nodes max weight must be {n_min_weight} or greater')

            nodes = int(self.nodes_number.text)
            if nodes < 1:
                raise ValueError('Nodes amount must be 1 or more')

            correlation = float(self.graph_correlation.text)
            if correlation < 0 or correlation > 1:
                raise ValueError('Correlation must be between 0 and 1')

            e_min_weight = int(self.edges_min_weight.text) if self.edges_min_weight.text else 1
            if e_min_weight < 1:
                raise ValueError('Edges min weight must be 1 or greater')

            e_max_weight = int(self.edges_max_weight.text) if self.edges_max_weight else max(e_min_weight, 9)
            if e_max_weight < e_min_weight:
                raise ValueError(f'Edges max weight must be {e_min_weight} or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct nodes amount!\n{" ".join(ve.args)}').open()

        else:
            self.parent_tab.generate(nodes)
