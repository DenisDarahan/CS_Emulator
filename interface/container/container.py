from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ObjectProperty

from CS_Emulator.graph import Graph
from .task_graph import TaskGraphTab
from .computer_system import ComputerSystemTab
from .modeling import ModelingTab
from .results import ResultsTab
from interface.popups import InfoPopup


class Container(BoxLayout):
    tabbed_panel: TabbedPanel = ObjectProperty()

    def __init__(self, task_graph: Graph, cs_graph: Graph, **kwargs):
        super().__init__(**kwargs)
        self.tabbed_panel.add_widget(TaskGraphTab(task_graph))
        self.tabbed_panel.add_widget(ComputerSystemTab(cs_graph))
        self.tabbed_panel.add_widget(ModelingTab(*self.tabbed_panel.tab_list[::-1]))
        self.tabbed_panel.add_widget(ResultsTab(self.tabbed_panel.tab_list[-1]))
        self.tabbed_panel.default_tab = self.tabbed_panel.tab_list[-1]

    @staticmethod
    def show_help():
        InfoPopup('Помощь', 'Бог в помощь').open()

    # def exit_app(self):
    #     self.get_root_window()
