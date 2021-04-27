from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from interface.popups import ErrorPopup
from .queue_builder import QueueBuilder


class ResultsTab(TabbedPanelItem):
    layout: BoxLayout = ObjectProperty()

    def __init__(self, task_graph_tab: TabbedPanelItem, **kwargs):
        self.tg_tab = task_graph_tab
        super().__init__(**kwargs)

    def lab_02(self):
        if not self.tg_tab.nodes:
            ErrorPopup('Task graph not found!\nPlease, build task graph first').open()
            return

        data = self.tg_tab.graph.lab_02()
        headers = ['Node', 'T[sub]CR[i]i[/i]E[/sub]', 'T[sub]CR[i]i[/i]S[/sub]',
                   'E[sub][i]i[/i][/sub]', 'L[sub][i]i[/i][/sub]', 'E[sub][i]i[/i][/sub] - L[sub][i]i[/i][/sub]']
        values = ['t_end', 't_start', 'early', 'lately']
        results = ['diff']
        QueueBuilder(data, headers, values, results, self.layout).show()

    def lab_03(self):
        if not self.tg_tab.nodes:
            ErrorPopup('Task graph not found!\nPlease, build task graph first').open()
            return

        data = self.tg_tab.graph.lab_03()
        headers = ['Node', 'N[sub]CR[i]i[/i]E[/sub]', 'S[sub]V[i]i[/i][/sub]']
        values = []
        results = ['cpl', 'cons']
        QueueBuilder(data, headers, values, results, self.layout).show()

    def lab_04(self):
        if not self.tg_tab.nodes:
            ErrorPopup('Task graph not found!\nPlease, build task graph first').open()
            return

        data = self.tg_tab.graph.lab_04()
        headers = ['Node', 'N[sub]CR[i]i[/i]S[/sub]', 'Node weight']
        values = []
        results = ['cpl', 'weight']
        QueueBuilder(data, headers, values, results, self.layout).show()

    def lab_05(self):
        pass

    def lab_06(self):
        pass

    def lab_07(self):
        pass

    def lab_08(self):
        pass
