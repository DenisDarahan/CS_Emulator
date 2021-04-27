from kivy.uix.widget import WidgetException
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.input.motionevent import MotionEvent

from CS_Emulator.interface import ErrorPopup
from .popups import ProcessorAskAddLink


class Processor(BoxLayout):
    proc_menu: DropDown = ObjectProperty()
    proc_button: Button = ObjectProperty()

    # moving: bool = False

    def __init__(self, proc_id: int, parent_tab: TabbedPanelItem, proc_pos=None, **kwargs):
        self.proc_id = proc_id
        self.str_id = str(proc_id + 1)
        self.parent_tab = parent_tab
        self.parent_layout = parent_tab.layout
        self.proc_pos = proc_pos
        self.links = []

        super().__init__(**kwargs)
        self.bind(pos=self.redraw_links)

    def redraw_links(self, *_args):
        for link in self.links:
            link.draw_line()

    def on_touch_down(self, touch: MotionEvent):
        if self.collide_point(*touch.pos) and not touch.grab_list:
            touch.grab(self)

    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current is self:
            self.pos[0] = min(touch.x - touch.x % 50, self.parent.size[0] - self.parent.size[0] % 300)
            self.pos[1] = min(touch.y - touch.y % 50, self.parent.size[1] - self.parent.size[1] % 300)
            self.parent_tab.graph.nodes[self.proc_id].node_pos = self.pos
            # self.moving = True

    def on_touch_up(self, touch: MotionEvent):
        if self.collide_point(*touch.pos) and not touch.grab_list:
            try:
                self.proc_menu.open(self)
            except WidgetException:
                return

        elif touch.grab_current is self:
            touch.ungrab(self)
            # self.moving = False
            self.proc_menu.open(self)

    def ask_add_link(self):
        self.proc_menu.dismiss()
        if len(self.parent_tab.processors) < 2:
            ErrorPopup('Not enough processors!\nAdd at least 2 processors').open()
            return
        ProcessorAskAddLink(self.parent_tab, self).open()

    def remove(self):
        self.proc_menu.dismiss()
        self.parent_tab.remove_processor(self)
