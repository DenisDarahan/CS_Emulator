from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class EdgeAskWeight(Popup):
    edge_weight = ObjectProperty()

    def __init__(self, edge, **kwargs):
        super().__init__(**kwargs)
        self.edge = edge

    def set_weight(self):
        self.dismiss()

        try:
            weight = int(self.edge_weight.text)
            if weight < 1:
                raise ValueError('Weight must be 1 or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct edge weight!\n{" ".join(ve.args)}').open()

        else:
            self.edge.set_weight(weight)
