from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ObjectProperty

from graph import Graph
from .task_graph import TaskGraphTab
from .computer_system import ComputerSystemTab
from .modeling import ModelingTab
from .results import ResultsTab
from interface.popups import InfoPopup


class Container(BoxLayout):
    tabbed_panel: TabbedPanel = ObjectProperty()

    def __init__(self, task_graph: Graph, cs_graph: Graph, **kwargs):
        super().__init__(**kwargs)

        tg_tab = TaskGraphTab(task_graph)
        cs_tab = ComputerSystemTab(cs_graph)
        m_tab = ModelingTab(tg_tab, cs_tab)
        r_tab = ResultsTab(tg_tab, cs_tab, m_tab)

        self.tabbed_panel.add_widget(tg_tab)
        self.tabbed_panel.add_widget(cs_tab)
        self.tabbed_panel.add_widget(m_tab)
        self.tabbed_panel.add_widget(r_tab)

        self.tabbed_panel.default_tab = self.tabbed_panel.tab_list[-1]

    @staticmethod
    def show_help():
        InfoPopup('Помощь', 'Бог в помощь').open()

    # def exit_app(self):
    #     self.get_root_window()
