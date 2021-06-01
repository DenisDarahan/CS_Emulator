from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from ..table_labels import HeadLabel, ValueLabel, ResultLabel


class StatsResults(ScrollView):
    table: GridLayout = ObjectProperty()

    def __init__(self, parent_layout: BoxLayout, **kwargs):
        self.parent_layout = parent_layout
        super().__init__(**kwargs)
        self._init_table()

    def _init_table(self):
        self.parent_layout.clear_widgets()
        self.parent_layout.add_widget(self)
        self.table.rows = 1
        self.table.cols = 7

        self.table.add_widget(HeadLabel(text='Nodes count'))
        self.table.add_widget(HeadLabel(text='Correlation'))
        self.table.add_widget(HeadLabel(text='Queue'))
        self.table.add_widget(HeadLabel(text='Time'))
        self.table.add_widget(HeadLabel(text='Acceleration'))
        self.table.add_widget(HeadLabel(text='Sys Eff'))
        self.table.add_widget(HeadLabel(text='Alg Eff'))

    def add_row(self, nodes_count: int, correlation: float, queue: int, time: int, acc: float, sys_eff: float,
                alg_eff: float):
        self.table.rows += 1

        self.table.add_widget(ValueLabel(text=str(nodes_count)))
        self.table.add_widget(ValueLabel(text=str(correlation)))
        self.table.add_widget(ValueLabel(text=str(queue)))
        self.table.add_widget(ResultLabel(text=f'{time:.5f}'))
        self.table.add_widget(ResultLabel(text=f'{acc:.5f}'))
        self.table.add_widget(ResultLabel(text=f'{sys_eff:.5f}'))
        self.table.add_widget(ResultLabel(text=f'{alg_eff:.5f}'))
