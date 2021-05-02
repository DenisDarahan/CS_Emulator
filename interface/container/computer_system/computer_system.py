from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

from graph import Graph
from interface.popups import ErrorPopup
from .processor import Processor
from .link import Link, AskAddLink
from .popups import ComputerSystemSave, ComputerSystemSaveName, ComputerSystemLoadName


class ComputerSystemTab(TabbedPanelItem):
    layout: FloatLayout = ObjectProperty()
    validation: Label = ObjectProperty()

    processors: list = []
    links: list = []

    def __init__(self, graph: Graph, **kwargs):
        self.graph = graph
        self.system_types = ('MPP', 'SMP')
        self.system_type = self.system_types[0]
        super().__init__(**kwargs)

    def set_system_type(self, system_type: str):
        assert system_type in self.system_types, \
            f'Unknown computer system type! {system_type} given. Only {", ".join(self.system_types)} available'
        self.system_type = system_type

    def add_processor(self):
        new_processor = Processor(len(self.processors), self)

        self.graph.add_node(new_processor.proc_id, 0, new_processor.pos)
        self.layout.add_widget(new_processor)
        self.processors.append(new_processor)
        self.validate()

        return new_processor

    def validate(self):
        if self.graph.has_gaps():
            self.validation.text = '[color=ff0000]Not valid[/color]'
        else:
            self.validation.text = '[color=00ff00]Valid[/color]'

    def remove_processor(self, processor: Processor):
        self.processors.remove(processor)
        while processor.links:
            self.remove_link(processor.links[0])

        for _processor in self.processors:
            if _processor.proc_id > processor.proc_id:
                # _processor.proc_pos = _processor.pos
                _processor.proc_id -= 1
                _processor.str_id = str(_processor.proc_id + 1)
                _processor.proc_button.text = _processor.str_id

        self.graph.remove_node(processor.proc_id)
        self.layout.remove_widget(processor)

        if not self.layout.children:
            self.validation.text = 'Validation'

    def ask_add_link(self):
        if len(self.processors) < 2:
            ErrorPopup('Not enough processors!\nAdd at least 2 processors').open()
            return
        AskAddLink(self).open()

    def add_link(self, src_proc: Processor, dst_proc: Processor):
        new_link = Link(len(self.links), self, src_proc, dst_proc)

        self.graph.add_edge(new_link.link_id, 0, src_proc.proc_id, dst_proc.proc_id)
        self.layout.add_widget(new_link)
        self.links.append(new_link)
        self.validate()

        src_proc.links.append(new_link)
        dst_proc.links.append(new_link)

        return new_link

    def remove_link(self, link: Link):
        self.links.remove(link)
        link.src_proc.links.remove(link)
        link.dst_proc.links.remove(link)

        for _link in self.links:
            if _link.link_id > link.link_id:
                _link.link_id -= 1

        self.graph.remove_edge(link.link_id)
        self.layout.remove_widget(link)
        self.validate()

    def clear_system(self):
        self.graph.clear()
        self.processors.clear()
        self.links.clear()
        self.layout.clear_widgets()

    def ask_load(self):
        if self.layout.children:
            ComputerSystemSave(self, self.ask_load_name).open()
            return
        self.ask_load_name()

    def ask_load_name(self):
        ComputerSystemLoadName(self).open()

    def load(self, name: str):
        self.clear_system()
        self.display_graph(*self.graph.load(name))

    def ask_save_name(self, callback=None):
        if not self.layout.children:
            ErrorPopup('System is empty').open()
            return
        ComputerSystemSaveName(self, callback).open()

    def save(self, name: str, callback=None):
        self.graph.save(name, 2, 2)

        if callback is not None:
            callback()

    def display_graph(self, graph: Graph, _scale_level: [tuple, list]):
        for p_node in graph.nodes:
            new_proc = Processor(p_node.node_id, self, p_node.node_pos)
            self.layout.add_widget(new_proc)
            self.processors.append(new_proc)

        for l_edge in graph.edges:
            src_proc = self.processors[l_edge.src_node.node_id]
            dst_proc = self.processors[l_edge.dst_node.node_id]

            new_link = Link(l_edge.edge_id, self, src_proc, dst_proc)
            self.layout.add_widget(new_link)
            self.links.append(new_link)

            src_proc.links.append(new_link)
            dst_proc.links.append(new_link)
