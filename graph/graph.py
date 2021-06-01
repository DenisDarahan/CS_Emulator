import json
from random import randint

import networkx as nx

from .node import Node
from .edge import Edge
from .encoder import Encoder
from config import DUMP_PATH


class Graph:
    NODE_MIN_WEIGHT: int = 1
    NODE_MAX_WEIGHT: int = 9
    EDGE_MIN_WEIGHT: int = 1
    EDGE_MAX_WEIGHT: int = 9

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

    def add_random_edge(self, min_weight: int, max_weight: int):
        edges = [(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges]

        counter = 0
        while counter < 999:
            src = randint(0, len(self.nodes) - 2)
            dst = randint(src, len(self.nodes) - 1)  # if dst > src cycles cannot be there
            if src == dst:
                counter += 1
                continue

            if (src, dst) in edges:
                self.edges[edges.index((src, dst))].weight += randint(min_weight, max_weight)
            else:
                self.add_edge(len(self.edges), randint(min_weight, max_weight), src, dst)
            break

    def get_edge(self, src: Node, dst: Node) -> Edge:
        for edge in self.edges:
            if edge.src_node is src and edge.dst_node is dst:
                return edge
        raise ValueError('Edge not found')

    def remove_edge(self, edge_id: int):
        edge = self.edges.pop(edge_id)

        self.adj_matrix[edge.src_node.node_id][edge.dst_node.node_id] = 0
        self.adj_matrix[edge.dst_node.node_id][edge.src_node.node_id] = 0

        for _edge in self.edges:
            if _edge.edge_id > edge.edge_id:
                _edge.edge_id -= 1

    def set_edge_weight(self, edge_id: int, edge_weight: int):
        self.edges[edge_id].weight = edge_weight

    def get_correlation(self):
        nodes_weight = sum(node.weight for node in self.nodes)
        edges_weight = sum(edge.weight for edge in self.edges)
        return nodes_weight / (nodes_weight + edges_weight)

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

    def generate(self, n_min_weight: int, n_max_weight: int, nodes_number: int, correlation: float,
                 e_min_weight: int, e_max_weight: int, layout_size: tuple, scale_level: list, directed: bool = True):
        self.clear()

        graph = self._generate(nodes_number, directed)
        levels = self.assign_level(graph.adj)
        nodes_positions = self._generate_positions(levels, layout_size, scale_level)

        for src_node_id in sorted(graph):
            self.add_node(src_node_id, randint(n_min_weight, n_max_weight), nodes_positions[src_node_id])

        nodes_weight = sum(node.weight for node in self.nodes)
        edges_weight = nodes_weight / correlation - nodes_weight

        edge_id = 0
        e_max_weight = e_max_weight if e_max_weight is not None else n_max_weight // correlation + e_min_weight
        for src_node_id in graph.adj:
            for dst_node_id in graph.adj[src_node_id]:
                current_correlation = round(edges_weight - sum(edge.weight for edge in self.edges))
                if self.edges and current_correlation < 0:
                    try:
                        self.set_edge_weight(edge_id - 1, self.edges[edge_id - 1].weight + current_correlation)
                    except IndexError:
                        print(self.edges, edge_id, correlation, current_correlation)
                        exit(1)
                    current_correlation = 0

                if current_correlation == 0:
                    return self, scale_level

                self.add_edge(edge_id, randint(e_min_weight, e_max_weight), src_node_id, dst_node_id)
                edge_id += 1

        counter = 0
        while (edges_weight - sum(edge.weight for edge in self.edges)) > 0 and counter < 99999:
            self.add_random_edge(e_min_weight, e_max_weight)
            counter += 1

        return self, scale_level

    def _generate(self, nodes_number: int, directed: bool) -> nx.DiGraph:
        graph = nx.gnp_random_graph(nodes_number, 0.7, directed=directed)
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

        with open(DUMP_PATH / f'{self.graph_type}_{name}.json', 'w') as dump:
            json.dump(data, dump, ensure_ascii=False, indent=4, cls=Encoder)

    def load(self, name: str) -> tuple:
        self.clear()

        with open(DUMP_PATH / f'{self.graph_type}_{name}.json', 'r') as dump:
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
        result: dict = {'nodes': {src: {} for src in self.nodes}, 'CPL': 0, 'queue': []}

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

        result: dict = {'nodes': {src: {} for src in self.nodes}, 'CPL': 0, 'queue': []}

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

        result: dict = {'nodes': {src: {} for src in self.nodes}, 'CPL': 0, 'queue': []}

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

    @staticmethod
    def count_modeling_params(task_graph, cs_graph, model_results: dict = None, time: int = 1):
        time = model_results['time'] if model_results else time
        acc = sum(task.weight for task in task_graph.nodes) / time if time else 1
        sys_eff = acc / len(cs_graph.nodes)
        alg_eff = task_graph.critical_path_length() / time
        return time, acc, sys_eff, alg_eff

    def critical_path_length(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([node.node_id for node in self.nodes])
        graph.add_edges_from([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])
        return max([max(paths.values()) for _node, paths in dict(nx.all_pairs_dijkstra_path_length(graph)).items()])

    def shortest_path(self, src: Node, dst: Node):
        graph = nx.Graph()
        graph.add_nodes_from([node.node_id for node in self.nodes])
        graph.add_edges_from([(edge.src_node.node_id, edge.dst_node.node_id) for edge in self.edges])
        return nx.single_source_dijkstra(graph, src.node_id, dst.node_id)[1]

    def lab_06(self, queue: list, cs, _links_count: int = 1, duplex: bool = False):
        processors = {proc: {'task': None, 'memory': []} for proc in cs.nodes}  # task = {'task': task, 'start': int}
        proc_logs = {}  # proc_logs = {task: {'proc': proc, 'start': int}}

        link_queue = []  # link_task = [{(src_proc, dst_proc): task}, {(src_proc, dst_proc): task}]
        if duplex:
            link_logs = {(link.src_node, link.dst_node): [] for link in cs.edges}
            link_logs.update({(link.dst_node, link.src_node): [] for link in cs.edges})
        else:
            link_logs = {frozenset([link.src_node, link.dst_node]): [] for link in cs.edges}
        # link_logs = {(src_proc, dst_proc): [{'src': src_task, 'dst': dst_task, 'start': int, 'end': int}]}

        tick = 0

        # print(*[task.node_id for task in queue])

        while queue or link_queue or any([(processors[p]['task'] or processors[p]['memory']) for p in processors]):
            # print(f'Tick {tick} :: {[t.node_id for t in queue]}')

            for proc in processors:
                if processors[proc]['task'] and \
                        processors[proc]['task']['task'].weight <= tick - processors[proc]['task']['start']:
                    proc_logs[processors[proc]['task']['task']] = {'proc': proc,
                                                                   'start': processors[proc]['task']['start']}
                    # print(f'[+] Task {processors[proc]["task"]["task"].node_id} done')
                    processors[proc]['task'] = None

            _queue = []
            while queue:
                task = queue.pop(0)

                free_processors = [proc for proc in processors if not processors[proc]['task']]
                if free_processors:

                    try:
                        next_processor = min(
                            free_processors,
                            key=lambda p: sum(
                                self.get_edge(self.nodes[_src_task_id], task).weight *
                                len(cs.shortest_path(proc_logs[self.nodes[_src_task_id]]['proc'], p))
                                for _src_task_id, _is_anc in enumerate(self.adj_matrix[task.node_id][:task.node_id])
                                if _is_anc
                            )
                        )

                    except (KeyError, IndexError):
                        _queue.append(task)

                    else:
                        possible_ancestors = self.adj_matrix[task.node_id][:task.node_id]
                        if not any(possible_ancestors):
                            processors[next_processor]['task'] = {'task': task, 'start': tick}
                            # print(f'Task {task.node_id} ({task.weight}) -> Proc: {next_processor.node_id}')
                            continue

                        for src_task_id, is_anc in enumerate(possible_ancestors):
                            if is_anc:
                                path = cs.shortest_path(proc_logs[self.nodes[src_task_id]]['proc'], next_processor)
                                # path in task can be empty!
                                link_queue.append({
                                    'path': [{'link': ((cs.nodes[path[i]], cs.nodes[path[i + 1]]) if duplex else
                                                       frozenset((cs.nodes[path[i]], cs.nodes[path[i + 1]]))),
                                              'start': 0}
                                             for i in range(len(path) - 1)],
                                    'src': self.nodes[src_task_id], 'dst': task, 'target': next_processor,
                                    'weight': self.get_edge(self.nodes[src_task_id], task).weight
                                })

                        # print(f'[Ancestors done] {tick} {task.node_id}')
                        # print(f'Task {task.node_id} ({task.weight}) -> Link queue: {link_queue[-1]}')

                else:
                    _queue.append(task)
            queue = _queue

            _link_queue = []
            while link_queue:
                link_task: dict = link_queue.pop(0)
                # print(link_task)

                if link_task['path'] and link_task['path'][0]['start'] and \
                        tick - link_task['path'][0]['start'] >= link_task['weight']:
                    # print(f'[=>] {link_task["src"].node_id} -> {link_task["dst"].node_id} '
                    #       f'{[n.node_id for n in link_task["path"][0]["link"]]}')
                    _path = link_task['path'].pop(0)
                    link_logs[_path['link']].append({
                        'src': link_task['src'], 'dst': link_task['dst'], 'start': _path['start'], 'end': tick
                    })

                if not link_task['path']:
                    if not any([_lt['dst'] == link_task['dst'] for _lt in link_queue + _link_queue]):
                        processors[link_task['target']]['memory'].append({'task': link_task['dst'], 'start': None})
                        # print(f'Task {link_task["dst"].node_id} -> Memory Proc: {link_task["target"].node_id}')
                        # print(f'[To memory] {tick} {link_task["dst"].node_id}')
                    continue

                _link_queue.append(link_task)
                if link_task['path'] and not link_task['path'][0]['start'] and \
                        not any([t['path'][0]['start'] for t in link_queue + _link_queue
                                 if t['path'] and t['path'][0]['link'] == link_task['path'][0]['link']]):
                    # print(f'[Start is 0] {tick} {link_task["dst"].node_id}')
                    link_task['path'][0]['start'] = tick
            link_queue = _link_queue

            for proc in processors:
                if not processors[proc]['task'] and processors[proc]['memory']:
                    processors[proc]['task'] = processors[proc]['memory'].pop(0)
                    processors[proc]['task']['start'] = tick
                    # print(f'Task {processors[proc]["task"]["task"].node_id} '
                    #       f'({processors[proc]["task"]["task"].weight}) -> Proc: {proc.node_id}')

            tick += 1
            # if tick == 100:
            #     break

        # print(queue)
        # print(link_queue)
        # print(processors)
        return {'proc': proc_logs, 'link': link_logs, 'time': tick - 1}
