from decimal import Decimal

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
import matplotlib.pyplot as plt

from interface.popups import ErrorPopup
from .queue_builder import QueueBuilder
from .stats_results import StatsResults
from .popups import AskStatsParams
from config import IMAGE_PATH


class ResultsTab(TabbedPanelItem):
    layout: BoxLayout = ObjectProperty()

    def __init__(self, task_graph_tab: TabbedPanelItem, computer_system_tab: TabbedPanelItem,
                 modeling_tab: TabbedPanelItem, **kwargs):
        self.tg_tab = task_graph_tab
        self.cs_tab = computer_system_tab
        self.m_tab = modeling_tab
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

    def lab_08(self):
        AskStatsParams(self).open()

    def run_stats(self, n_min_count: int, n_max_count: int, n_step: int, c_min: float, c_max: float, c_step: float,
                  n_min_weight: int, n_max_weight: int, g_count: int):

        if not (self.cs_tab.processors or self.cs_tab.is_valid()):
            ErrorPopup('Not valid computer system').open()
            return

        stats_results = StatsResults(self.layout)

        c_min = _c_min = Decimal(str(c_min))
        c_max = Decimal(str(c_max))
        c_step = Decimal(str(c_step))

        logs = {}

        while n_min_count <= n_max_count:
            logs[n_min_count] = {}

            while _c_min <= c_max:
                logs[n_min_count][_c_min] = {}

                for _g_index in range(g_count):
                    logs[n_min_count][_c_min][_g_index] = {}

                    graph, _scale_level = self.tg_tab.graph.generate(
                        n_min_weight, n_max_weight, n_min_count, float(_c_min), 1, 9, self.tg_tab.layout.size,
                        [self.tg_tab.x_scale, self.tg_tab.y_scale]
                    )

                    queues = [{'number': 2, 'func': graph.lab_02}, {'number': 4, 'func': graph.lab_03},
                              {'number': 8, 'func': graph.lab_04}]

                    for queue_builder in queues:
                        queue = queue_builder['func']()['queue']
                        model = self.tg_tab.graph.lab_06(queue, self.cs_tab.graph,
                                                         duplex=self.m_tab.links_duplex.active)
                        time, acc, sys_eff, alg_eff = graph.count_modeling_params(graph, self.cs_tab.graph, model)

                        logs[n_min_count][_c_min][_g_index][queue_builder['number']] = \
                            {'time': time, 'acc': acc, 'sys_eff': sys_eff, 'alg_eff': alg_eff}

                        print(f'{n_min_count}->{_c_min}->{_g_index}->{queue_builder["number"]}: '
                              f'{time} / {acc} / {sys_eff} / {alg_eff}')

                avg = {_q: {'time': 0, 'acc': 0, 'sys_eff': 0, 'alg_eff': 0} for _q in (2, 4, 8)}
                for qs in logs[n_min_count][_c_min].values():
                    for q in avg:
                        for p in avg[q]:
                            avg[q][p] += qs[q][p] / g_count

                logs[n_min_count][_c_min]['avg'] = {}
                for q in avg:
                    logs[n_min_count][_c_min]['avg'][q] = avg[q]
                    stats_results.add_row(n_min_count, _c_min, q, avg[q]['time'], avg[q]['acc'],
                                          avg[q]['sys_eff'], avg[q]['alg_eff'])

                    print(f'AVG {n_min_count}->{_c_min}->{q}: {avg[q]["time"]} / {avg[q]["acc"]} / '
                          f'{avg[q]["sys_eff"]} / {avg[q]["alg_eff"]}')

                _c_min += c_step

            _c_min = c_min
            n_min_count += n_step

        self.build_graphs(logs)

    @staticmethod
    def build_graphs(logs: dict):
        full_data: dict = {}
        x = list(logs[4].keys())

        for n_count in logs:
            full_data[n_count] = {q: {'acc': [], 'sys_eff': [], 'alg_eff': []} for q in (2, 4, 8)}

            for correlation in logs[n_count]:
                for queue in logs[n_count][correlation]['avg']:
                    full_data[n_count][queue]['acc'].append(logs[n_count][correlation]['avg'][queue]['acc'])
                    full_data[n_count][queue]['sys_eff'].append(logs[n_count][correlation]['avg'][queue]['sys_eff'])
                    full_data[n_count][queue]['alg_eff'].append(logs[n_count][correlation]['avg'][queue]['alg_eff'])

            print(full_data[n_count])

        for n_count in full_data:
            for queue in full_data[n_count]:
                plt.plot(x, full_data[n_count][queue]['acc'], label=f'Q alg {queue}')
            plt.legend()
            plt.grid()
            plt.savefig(IMAGE_PATH / f'acc-{n_count}.png')
            plt.clf()

        for n_count in full_data:
            for queue in full_data[n_count]:
                plt.plot(x, full_data[n_count][queue]['sys_eff'], label=f'Q alg {queue}')
            plt.legend()
            plt.grid()
            plt.savefig(IMAGE_PATH / f'sys_eff-{n_count}.png')
            plt.clf()

        for n_count in full_data:
            for queue in full_data[n_count]:
                plt.plot(x, full_data[n_count][queue]['alg_eff'], label=f'Q alg {queue}')
            plt.legend()
            plt.grid()
            plt.savefig(IMAGE_PATH / f'alg_eff-{n_count}.png')
            plt.clf()
