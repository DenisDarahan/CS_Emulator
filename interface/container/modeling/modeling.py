from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.properties import ObjectProperty
from kivy.input.motionevent import MotionEvent

from .model_labels import HeadLabel, TaskLabel  # , ForwardingLabel, EmptyLabel


class ModelingTab(TabbedPanelItem):
    stats_table: GridLayout = ObjectProperty()
    time_mark: Label = ObjectProperty()
    acceleration_mark: Label = ObjectProperty()
    efficiency_mark: Label = ObjectProperty()
    links_count: TextInput = ObjectProperty()
    io_proc: Switch = ObjectProperty()
    links_duplex: Switch = ObjectProperty()
    data_forwarding: Spinner = ObjectProperty()
    package_size: TextInput = ObjectProperty()

    def __init__(self, task_graph_tab: TabbedPanelItem, computer_system_tab: TabbedPanelItem, **kwargs):
        self.tg_tab = task_graph_tab
        self.cs_tab = computer_system_tab
        self.forwarding_types = ('MSG', 'CONV')
        self.forwarding_type = self.forwarding_types[0]
        super().__init__(**kwargs)

    def on_touch_down(self, touch: MotionEvent):
        self.get_root_window().children[-1].tabbed_panel.switch_to(self)
        if self.collide_point(*touch.pos):
            self.build_model()

    def build_model(self):
        self.stats_table.clear_widgets()
        self.stats_table.cols = len(self.cs_tab.processors) + 1

        # head
        self.stats_table.add_widget(HeadLabel(text='N'))
        for proc in self.cs_tab.processors:
            self.stats_table.add_widget(HeadLabel(text=f'P[sub]{proc.str_id}[/sub]'))

        # body
        step = 1
        for task in self.tg_tab.nodes:
            for _tick in range(task.node_weight):
                self.stats_table.rows += step == self.stats_table.rows
                self.stats_table.add_widget(HeadLabel(text=str(step)))
                for _ in self.cs_tab.processors:
                    self.stats_table.add_widget(TaskLabel(text=f'T[sub]{task.str_id}[/sub]'))
                step += 1

        self.stats_table.rows = step  # if previous `rows` was bigger than currently needed

        time, acc, eff = self.count_params()
        self.time_mark.text = f'Time: {time}'
        self.acceleration_mark.text = f'Acceleration: {acc:.2f}'
        self.efficiency_mark.text = f'Efficiency: {eff:.2f}'

    def count_params(self):
        time = self.stats_table.rows - 1
        acc = sum(task.node_weight for task in self.tg_tab.nodes) / time if time else 1
        eff = 1
        return time, acc, eff

    def set_forwarding_type(self, forwarding_type: str):
        assert forwarding_type in self.forwarding_types, \
            f'Unknown forwarding type! {forwarding_type} given. Only {", ".join(self.forwarding_types)} available'
        self.forwarding_type = forwarding_type
