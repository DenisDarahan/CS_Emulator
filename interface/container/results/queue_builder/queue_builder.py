from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

from ..table_labels import HeadLabel, ValueLabel, ResultLabel


class QueueBuilder(BoxLayout):
    result_table: GridLayout = ObjectProperty()
    cpl_label: Label = ObjectProperty()
    queue_label: Label = ObjectProperty()

    def __init__(self, data: dict, headers: list, values: list, results: list, parent_layout: BoxLayout, **kwargs):
        self.data = data
        self.headers = headers
        self.values = values
        self.results = results
        self.parent_layout = parent_layout

        super().__init__(**kwargs)
        self.result_table.cols = len(self.headers)

    def build_result_table(self):
        # head
        for col in self.headers:
            self.result_table.add_widget(HeadLabel(text=col))

        # body
        for node in sorted(self.data['nodes'], key=lambda i: i.node_id):
            self.result_table.rows += 1
            self.result_table.add_widget(HeadLabel(text=f'{node.node_id + 1}'))
            for value in self.values:
                self.result_table.add_widget(ValueLabel(text=f'{self.data["nodes"][node][value]}'))
            for result in self.results:
                self.result_table.add_widget(ResultLabel(text=f'{self.data["nodes"][node][result]}'))

        # footer
        self.cpl_label.text = f'Critical path length: {self.data["CPL"]}'
        self.queue_label.text = ', '.join([
            f'{node.node_id + 1}({", ".join([str(self.data["nodes"][node][result]) for result in self.results])})'
            for node in self.data['queue']
        ])

    def show(self):
        self.parent_layout.clear_widgets()
        self.build_result_table()
        self.parent_layout.add_widget(self)
