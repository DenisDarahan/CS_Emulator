from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from CS_Emulator.interface import ErrorPopup


class NodeAskWeight(Popup):
    node_weight: TextInput = ObjectProperty()

    def __init__(self, node, **kwargs):
        super().__init__(**kwargs)
        self.node = node

    def set_weight(self):
        self.dismiss()

        try:
            weight = int(self.node_weight.text)
            if weight < 1:
                raise ValueError('Weight must be 1 or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct node weight!\n{" ".join(ve.args)}').open()

        else:
            self.node.set_weight(weight)
