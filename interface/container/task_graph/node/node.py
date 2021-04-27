from kivy.uix.widget import WidgetException
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty
from kivy.input.motionevent import MotionEvent

from CS_Emulator.interface import ErrorPopup
from .popups import NodeAskWeight, NodeAskAddEdge


class Node(BoxLayout):
    node_button: Button = ObjectProperty()
    node_menu: DropDown = ObjectProperty()

    def __init__(self, node_id: int, node_weight: int, parent_tab: TabbedPanelItem, node_pos=None, **kwargs):
        self.node_id = node_id
        self.str_id = str(node_id + 1)
        self.node_weight = node_weight
        self.parent_tab = parent_tab
        self.parent_layout = parent_tab.layout
        self.node_pos = node_pos
        self.edges = []

        super().__init__(**kwargs)
        self.bind(pos=self.redraw_edges)

    def redraw_edges(self, *_args):
        for edge in self.edges:
            edge.draw_vector()

    def on_touch_down(self, touch: MotionEvent):
        if self.collide_point(*touch.pos) and not touch.grab_list:
            touch.grab(self)

    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current is self:
            self.pos[0] = min(touch.x - touch.x % 50, self.parent.size[0] - self.parent.size[0] % 300)
            self.pos[1] = min(touch.y - touch.y % 50, self.parent.size[1] - self.parent.size[1] % 300)
            self.parent_tab.graph.nodes[self.node_id].node_pos = self.pos

    def on_touch_up(self, touch: MotionEvent):
        if self.collide_point(*touch.pos) and not touch.grab_list:
            try:
                self.node_menu.open(self)
            except WidgetException:
                return

        elif touch.grab_current is self:
            touch.ungrab(self)

    def ask_weight(self):
        self.node_menu.dismiss()
        NodeAskWeight(self).open()

    def set_weight(self, weight: int):
        self.node_weight = weight
        self.node_button.text = f'{self.str_id} | {weight}'
        self.parent_tab.graph.set_node_weight(self.node_id, weight)

    def ask_add_edge(self):
        self.node_menu.dismiss()
        if len(self.parent_tab.nodes) < 2:
            ErrorPopup('Not enough nodes!\nAdd at least 2 nodes').open()
            return
        NodeAskAddEdge(self.parent_tab, self).open()

    def remove(self):
        self.node_menu.dismiss()
        self.parent_tab.remove_node(self)
