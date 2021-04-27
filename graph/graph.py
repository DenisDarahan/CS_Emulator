import json
from random import randint

import networkx as nx

from .node import Node
from .edge import Edge
from .encoder import Encoder
from CS_Emulator.config import DUMP_PATH


class Graph:

    def __init__(self, graph_type: str):
        self.graph_type = graph_type
        self.name = None
        self.nodes = []
        self.edges = []
        self.adj_matrix = []

    def print_adj(self):
        print('\n'.join([' '.join([str(elem) for elem in row]) for row in self.adj_matrix]))

    def add_node(self, node_id: int, node_weight: int, node_pos: [tuple, list]):
        assert len(self.nodes) == node_id, f'Node error! Wrong node id ({node_id})'

        self.nodes.append(Node(node_id, node_weight, tuple(node_pos)))
        for row in self.adj_matrix:
            row.append(0)
        self.adj_matrix.append([0 for _ in range(len(self.adj_matrix) + 1)])

    def remove_node(self, node_id: int):
        self.nodes.pop(node_id)

        self.adj_matrix.pop(node_id)
        for row in self.adj_matrix:
            row.pop(node_id)

        for node in self.nodes:
            if node.node_id > node_id:
                node_id -= 1

    def set_node_weight(self, node_id: int, node_weight: int):
        self.nodes[node_id].weight = node_weight

    def add_edge(self, edge_id: int, edge_weight: int, src_node_id: int, dst_node_id: int):
        assert len(self.edges) == edge_id, f'Edge error! Wrong edge id ({edge_id})'

        self.edges.append(Edge(edge_id, edge_weight, self.nodes[src_node_id], self.nodes[dst_node_id]))
        self.adj_matrix[src_node_id][dst_node_id] = 1
        self.adj_matrix[dst_node_id][src_node_id] = 1

    def remove_edge(self, edge_id: int):
        edge = self.edges.pop(edge_id)

        self.adj_matrix[edge.src_node.node_id][edge.dst_node.node_id] = 0
        self.adj_matrix[edge.dst_node.node_id][edge.src_node.node_id] = 0

        for _edge in self.edges:
            if _edge.edge_id > edge.edge_id:
                _edge.edge_id -= 1

    def set_edge_weight(self, edge_id: int, edge_weight: int):
        self.edges[edge_id].weight = edge_weight

    def has_cycles(self) -> bool:
        graph = nx.DiGraph([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])
        return not nx.is_directed_acyclic_graph(graph)

    def has_gaps(self) -> bool:
        if len(self.nodes) <= 1:
            return False

        graph = nx.Graph()
        graph.add_nodes_from([node.node_id for node in self.nodes])
        graph.add_edges_from([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])

        if not graph.edges:
            return True

        paths = nx.single_source_dijkstra_path_length(graph, 0)
        return not all([dst.node_id in paths for dst in self.nodes])

    def generate(self, nodes_number: int, layout_size: tuple, scale_level: list, directed: bool = True):
        graph = self._generate(nodes_number, directed)
        levels = self.assign_level(graph.adj)
        nodes_positions = self._generate_positions(levels, layout_size, scale_level)

        for src_node_id in sorted(graph):
            self.add_node(src_node_id, randint(1, 9), nodes_positions[src_node_id])

        edge_id = 0
        for src_node_id in graph.adj:
            for dst_node_id in graph.adj[src_node_id]:
                self.add_edge(edge_id, randint(1, 9), src_node_id, dst_node_id)
                edge_id += 1

        return self, scale_level

    def _generate(self, nodes_number: int, directed: bool) -> nx.DiGraph:
        graph = nx.gnp_random_graph(nodes_number, 0.5, directed=directed)
        dag = nx.DiGraph([(src, dst) for (src, dst) in graph.edges() if src < dst])

        if not nx.is_directed_acyclic_graph(dag) or set(dag.nodes) != set(range(nodes_number)):
            return self._generate(nodes_number, directed)
        return dag

    def assign_level(self, graph: dict) -> dict:
        for src_node_id in range(len(self.nodes)):
            graph[src_node_id] = [dst_node_id for dst_node_id in range(len(self.nodes[src_node_id]))
                                  if self.nodes[src_node_id][dst_node_id]]

        levels = {}
        for src_node_id in graph:
            self._assign_level(graph, src_node_id, levels)
        return levels

    def _assign_level(self, graph, src_node_id, levels) -> int:
        if src_node_id not in levels:
            if src_node_id not in graph or not graph[src_node_id]:
                levels[src_node_id] = 0
            else:
                levels[src_node_id] = max(self._assign_level(graph, dst_node_id, levels) + 1
                                          for dst_node_id in graph[src_node_id])
        return levels[src_node_id]

    @staticmethod
    def _generate_positions(levels: dict, layout_size: tuple, scale_level: list) -> dict:
        while len(levels) * 50 > layout_size[0] // scale_level[0]:
            layout_size[0] += layout_size[0] // scale_level[0]
            layout_size[1] += layout_size[1] // scale_level[1]

        level_groups = {lvl: [node_id for node_id, _lvl in levels.items() if _lvl == lvl] for lvl in levels.values()}
        nodes_positions = {}
        for level in sorted(level_groups, reverse=True):
            for index, node_id in enumerate(level_groups[level]):
                _level = len(level_groups) - level - 1
                nodes_positions[node_id] = (
                    index * 200 + 100 + 50 * (_level % 2),
                    layout_size[1] - 150 - ((layout_size[1] - 150) % 50) - _level * 200
                )

        return nodes_positions

    def save(self, name: str, x_scale: int, y_scale: int):
        data = {
            'graph_type': self.graph_type,
            'name': name,
            'x_scale': x_scale,
            'y_scale': y_scale,
            'nodes': self.nodes,
            'edges': self.edges
        }

        with open(f'{DUMP_PATH}/{self.graph_type}_{name}.json', 'w') as dump:
            json.dump(data, dump, ensure_ascii=False, indent=4, cls=Encoder)

    def load(self, name: str) -> tuple:
        self.clear()

        with open(f'{DUMP_PATH}/{self.graph_type}_{name}.json', 'r') as dump:
            graph = json.load(dump)

        self.name = graph['name']
        x_scale = graph['x_scale']
        y_scale = graph['y_scale']

        for node in graph['nodes']:
            self.add_node(**node)

        for edge in graph['edges']:
            self.add_edge(**edge)

        return self, (x_scale, y_scale)

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.adj_matrix.clear()

    def lab_02(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([node.node_id for node in self.nodes])
        graph.add_edges_from([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])

        reverse_graph = graph.reverse()
        result = {'nodes': {src: {} for src in self.nodes}, 'CPL': 0, 'queue': []}

        for src in self.nodes:
            destinations = [dst.node_id for dst in self.nodes]
            destinations.remove(src.node_id)

            paths = nx.all_simple_paths(graph, src.node_id, destinations)
            paths_weights = [sum(self.nodes[dst_node_id].weight for dst_node_id in path) for path in paths]
            paths_weights.append(src.weight)

            reverse_paths = nx.all_simple_paths(reverse_graph, src.node_id, destinations)
            reverse_paths_weights = [sum(self.nodes[dst_node_id].weight
                                         for dst_node_id in reverse_path if dst_node_id != src.node_id)
                                     for reverse_path in reverse_paths]
            reverse_paths_weights.append(0)

            result['nodes'][src].update({'t_end': max(paths_weights), 't_start': max(reverse_paths_weights)})

        result['CPL'] = max(value['t_end'] for value in result['nodes'].values())

        for node in result['nodes']:
            result['nodes'][node]['early'] = result['nodes'][node]['t_start'] + 1
            result['nodes'][node]['lately'] = result['CPL'] - result['nodes'][node]['t_end'] + 1
            result['nodes'][node]['diff'] = result['nodes'][node]['lately'] - result['nodes'][node]['early']

        result['queue'] = sorted(result['nodes'], key=lambda i: result['nodes'][i]['diff'])
        return result

    def lab_03(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([node.node_id for node in self.nodes])
        graph.add_edges_from([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])

        result = {'nodes': {src: {} for src in self.nodes}, 'CPL': 0, 'queue': []}

        for src in self.nodes:
            destinations = [dst.node_id for dst in self.nodes]
            destinations.remove(src.node_id)

            paths = nx.all_simple_paths(graph, src.node_id, destinations)
            paths_weights = [len(path) for path in paths]
            paths_weights.append(1)

            result['nodes'][src].update({'cpl': max(paths_weights), 'cons': sum(self.adj_matrix[src.node_id])})

        result['queue'] = sorted(result['nodes'], key=lambda i: result['nodes'][i]['cpl'], reverse=True)
        result['CPL'] = result['nodes'][result['queue'][0]]['cpl']

        temp_node = result['queue'][0]
        start, stop = 0, 1

        # inner sort
        for node in result['queue'][1:]:
            if result['nodes'][temp_node]['cpl'] == result['nodes'][node]['cpl']:
                stop += 1
                continue

            result['queue'][start:stop] = sorted(
                result['queue'][start:stop], key=lambda i: result['nodes'][i]['cons'], reverse=True
            )
            start = stop
            stop += 1
            temp_node = result['queue'][start]

        result['queue'][start:stop] = sorted(
            result['queue'][start:stop], key=lambda i: result['nodes'][i]['cons'], reverse=True
        )

        return result

    def lab_04(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([node.node_id for node in self.nodes])
        graph.add_edges_from([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])
        graph = graph.reverse()

        result = {'nodes': {src: {} for src in self.nodes}, 'CPL': 0, 'queue': []}

        for src in self.nodes:
            destinations = [dst.node_id for dst in self.nodes]
            destinations.remove(src.node_id)

            paths = nx.all_simple_paths(graph, src.node_id, destinations)
            paths_weights = [len(path) - 1 for path in paths]
            paths_weights.append(0)

            result['nodes'][src].update({'cpl': max(paths_weights), 'weight': src.weight})

        result['queue'] = sorted(result['nodes'], key=lambda i: result['nodes'][i]['cpl'])
        result['CPL'] = result['nodes'][result['queue'][-1]]['cpl']

        temp_node = result['queue'][0]
        start, stop = 0, 1

        # inner sort
        for node in result['queue'][1:]:
            if result['nodes'][temp_node]['cpl'] == result['nodes'][node]['cpl']:
                stop += 1
                continue

            result['queue'][start:stop] = sorted(
                result['queue'][start:stop], key=lambda i: result['nodes'][i]['weight'], reverse=True
            )
            start = stop
            stop += 1
            temp_node = result['queue'][start]

        result['queue'][start:stop] = sorted(
            result['queue'][start:stop], key=lambda i: result['nodes'][i]['weight'], reverse=True
        )

        return result
