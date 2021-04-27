from math import sqrt

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanelItem


class Link(BoxLayout):
    link_menu: DropDown = ObjectProperty()
    link_button: Button = ObjectProperty()

    def __init__(self, link_id: int, parent_tab: TabbedPanelItem, src_proc, dst_proc, **kwargs):
        self.link_id = link_id
        self.parent_tab = parent_tab
        self.src_proc = src_proc
        self.dst_proc = dst_proc

        super().__init__(**kwargs)
        self.draw_line()
        self.bind(pos=self.draw_line)

    def draw_line(self, *_args):
        distance_x = self.dst_proc.pos[0] - self.src_proc.pos[0]
        distance_y = self.dst_proc.pos[1] - self.src_proc.pos[1]
        distance = sqrt(distance_x ** 2 + distance_y ** 2)

        self.size = (abs(distance_x), abs(distance_y))
        # self.link_button.pos = (self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2)

        line = self.link_button.canvas.before.get_group('line')[0]
        line.points = (
            self.src_proc.pos[0] + 73 + 75 * distance_x / (0 ** distance + distance),
            self.src_proc.pos[1] + 73 + 75 * distance_y / (0 ** distance + distance),
            self.dst_proc.pos[0] + 73 - 75 * distance_x / (0 ** distance + distance),
            self.dst_proc.pos[1] + 73 - 75 * distance_y / (0 ** distance + distance)
        )

    def remove(self):
        self.link_menu.dismiss()
        self.parent_tab.remove_link(self)
