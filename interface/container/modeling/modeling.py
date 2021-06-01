from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.properties import ObjectProperty
from kivy.input.motionevent import MotionEvent

from .model_labels import HeadLabel, TaskLabel, ForwardingLabel, EmptyLabel
from .popups import AskQueue
from interface.popups import ErrorPopup


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
        if self.collide_point(*touch.pos) and not self.stats_table.children:
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
        self.display_params()

    def count_params(self):
        time = self.stats_table.rows - 1
        acc = sum(task.node_weight for task in self.tg_tab.nodes) / time if time else 1
        eff = acc / len(self.cs_tab.processors)
        return time, acc, eff

    def display_params(self):
        time, acc, eff = self.count_params()
        self.time_mark.text = f'Time: {time}'
        self.acceleration_mark.text = f'Acceleration: {acc:.2f}'
        self.efficiency_mark.text = f'Efficiency: {eff:.2f}'

    def set_forwarding_type(self, forwarding_type: str):
        assert forwarding_type in self.forwarding_types, \
            f'Unknown forwarding type! {forwarding_type} given. Only {", ".join(self.forwarding_types)} available'
        self.forwarding_type = forwarding_type

    def lab_06(self):
        if self.cs_tab.system_type != 'MPP':
            ErrorPopup('Wrong system type!\nMPP expected, got SMP').open()
            return

        if not (self.cs_tab.processors or self.cs_tab.is_valid()):
            ErrorPopup('Not valid computer system').open()
            return

        AskQueue(self, self._lab_06).open()

    def _lab_06(self, queue_builder):
        queue = queue_builder()['queue']

        self.io_proc.active = True
        model = self.tg_tab.graph.lab_06(queue, self.cs_tab.graph, duplex=self.links_duplex.active)

        self.stats_table.clear_widgets()
        self.stats_table.cols = (len(self.cs_tab.processors) + 1 +
                                 len(self.cs_tab.links) * (self.links_duplex.active + 1))
        self.stats_table.rows = 1

        self.stats_table.add_widget(HeadLabel(text='N'))
        for proc in self.cs_tab.processors:
            self.stats_table.add_widget(HeadLabel(text=f'P[sub]{proc.str_id}[/sub]'))

        if self.links_duplex.active:
            for link in self.cs_tab.links:
                self.stats_table.add_widget(HeadLabel(text=f'P[sub]{link.src_proc.str_id}[/sub] -> '
                                                           f'P[sub]{link.dst_proc.str_id}[/sub]'))
                self.stats_table.add_widget(HeadLabel(text=f'P[sub]{link.dst_proc.str_id}[/sub] -> '
                                                           f'P[sub]{link.src_proc.str_id}[/sub]'))
        else:
            for link in self.cs_tab.links:
                _proc = sorted([link.src_proc, link.dst_proc], key=lambda i: i.proc_id)
                self.stats_table.add_widget(HeadLabel(text=f'P[sub]{_proc[0].str_id}[/sub] <-> '
                                                           f'P[sub]{_proc[1].str_id}[/sub]'))

        _proc = {t: {p: None for p in self.cs_tab.graph.nodes} for t in range(model['time'])}
        for _task in model['proc']:
            for t in range(model['proc'][_task]['start'], model['proc'][_task]['start'] + _task.weight):
                _proc[t][model['proc'][_task]['proc']] = _task

        _link = {t: {_l: None for _l in model['link']} for t in range(model['time'])}
        for _l in model['link']:
            for _task in sorted(model['link'][_l], key=lambda i: i['start']):
                for t in range(_task['start'], _task['end']):
                    _link[t][_l] = (_task['src'], _task['dst'], _task['end'] - _task['start'])

        for tick in range(model['time']):
            self.stats_table.rows += 1

            self.stats_table.add_widget(HeadLabel(text=str(tick + 1)))
            for p in self.cs_tab.graph.nodes:
                try:
                    self.stats_table.add_widget(TaskLabel(
                        text=f'T[sub]{_proc[tick][p].node_id + 1}[/sub] ({_proc[tick][p].weight})'
                    ))
                except (KeyError, IndexError, AttributeError, TypeError):
                    self.stats_table.add_widget(EmptyLabel())

            for _l in model['link']:
                try:
                    self.stats_table.add_widget(ForwardingLabel(
                        text=f'T[sub]{_link[tick][_l][0].node_id + 1}[/sub]->'
                             f'T[sub]{_link[tick][_l][1].node_id + 1}[/sub] ({_link[tick][_l][2]})'
                    ))
                except (KeyError, IndexError, AttributeError, TypeError):
                    self.stats_table.add_widget(EmptyLabel())

        self.display_params()

        # for proc in self.cs_tab.graph.nodes:
        #     print(f'Proc {proc.node_id}')
        #     for task in sorted(filter(lambda i: model['proc'][i]['proc'] is proc, model['proc']),
        #                        key=lambda i: model['proc'][i]['start']):
        #         print(f'Tick {model["proc"][task]["start"]}: {task.node_id}({task.weight})')
        #     print()
        #
        # for link in model['link']:
        #     _link = list(link)
        #     print(f'Link {_link[0].node_id} - {_link[1].node_id}')
        #     for send_task in sorted(model['link'][link], key=lambda i: i['start']):
        #         print(f'Tick {send_task["start"]} - {send_task["end"]}: '
        #               f'{send_task["src"].node_id} -> {send_task["dst"].node_id}')
        #     print()

    @staticmethod
    def lab_07():
        ErrorPopup('Not Implemented Error').open()

    # def lab_07(self):
    #     if self.cs_tab.system_type != 'MPP':
    #         ErrorPopup('Wrong system type!\nMPP expected, got SMP').open()
    #         return
    #
    #     if not (self.cs_tab.processors or self.cs_tab.is_valid()):
    #         ErrorPopup('Not valid computer system').open()
    #         return
    #
    #     AskQueue(self, self._lab_07).open()
    #
    # def _lab_07(self, queue_builder):
    #     queue = queue_builder()['queue']
    #
    #     self.io_proc.active = True
    #     model = self.tg_tab.graph.lab_06(queue, self.cs_tab.graph, duplex=self.links_duplex.active)
    #
    #     self.stats_table.clear_widgets()
    #     self.stats_table.cols = (len(self.cs_tab.processors) + 1 +
    #                              len(self.cs_tab.links) * (self.links_duplex.active + 1))
    #     self.stats_table.rows = 1
    #
    #     self.stats_table.add_widget(HeadLabel(text='N'))
    #     for proc in self.cs_tab.processors:
    #         self.stats_table.add_widget(HeadLabel(text=f'P[sub]{proc.str_id}[/sub]'))
    #
    #     if self.links_duplex.active:
    #         for link in self.cs_tab.links:
    #             self.stats_table.add_widget(HeadLabel(text=f'P[sub]{link.src_proc.str_id}[/sub] -> '
    #                                                        f'P[sub]{link.dst_proc.str_id}[/sub]'))
    #             self.stats_table.add_widget(HeadLabel(text=f'P[sub]{link.dst_proc.str_id}[/sub] -> '
    #                                                        f'P[sub]{link.src_proc.str_id}[/sub]'))
    #     else:
    #         for link in self.cs_tab.links:
    #             _proc = sorted([link.src_proc, link.dst_proc], key=lambda i: i.proc_id)
    #             self.stats_table.add_widget(HeadLabel(text=f'P[sub]{_proc[0].str_id}[/sub] <-> '
    #                                                        f'P[sub]{_proc[1].str_id}[/sub]'))
    #
    #     _proc = {t: {p: None for p in self.cs_tab.graph.nodes} for t in range(model['time'])}
    #     for _task in model['proc']:
    #         for t in range(model['proc'][_task]['start'], model['proc'][_task]['start'] + _task.weight):
    #             _proc[t][model['proc'][_task]['proc']] = _task
    #
    #     _link = {t: {_l: None for _l in model['link']} for t in range(model['time'])}
    #     for _l in model['link']:
    #         for _task in sorted(model['link'][_l], key=lambda i: i['start']):
    #             for t in range(_task['start'], _task['end']):
    #                 _link[t][_l] = (_task['src'], _task['dst'])
    #
    #     for tick in range(model['time']):
    #         self.stats_table.rows += 1
    #
    #         self.stats_table.add_widget(HeadLabel(text=str(tick + 1)))
    #         for p in self.cs_tab.graph.nodes:
    #             try:
    #                 self.stats_table.add_widget(TaskLabel(text=f'T[sub]{_proc[tick][p].node_id + 1}[/sub]'))
    #             except (KeyError, IndexError, AttributeError, TypeError):
    #                 self.stats_table.add_widget(EmptyLabel())
    #
    #         for _l in model['link']:
    #             try:
    #                 self.stats_table.add_widget(ForwardingLabel(
    #                     text=f'T[sub]{_link[tick][_l][0].node_id + 1}[/sub]->'
    #                          f'T[sub]{_link[tick][_l][1].node_id + 1}[/sub] '
    #                          f'({model["proc"][_link[tick][_l][0]]["proc"].node_id + 1}->'
    #                          f'{model["proc"][_link[tick][_l][1]]["proc"].node_id + 1})'
    #                 ))
    #             except (KeyError, IndexError, AttributeError, TypeError):
    #                 self.stats_table.add_widget(EmptyLabel())
    #
    #     self.display_params()
