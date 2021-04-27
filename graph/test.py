import matplotlib.pyplot as plt
import networkx as nx

from random import randint, choice


class Graph:

    def __init__(self, number_nodes=15):
        self.number_nodes = number_nodes
        self.nodes = [node for node in range(self.number_nodes)]
        self.edges = []
        self.levels = []

    def generate_nodes(self):
        counter = 0
        copy_number = self.number_nodes
        while copy_number:
            try:
                level_population = randint(randint(1, copy_number // 4),
                                           randint(copy_number // 4, copy_number // 2))
            except ValueError:
                level_population = copy_number
            level = []
            for _ in range(level_population):
                level.append(counter)
                counter += 1
            self.levels.append(level)
            copy_number -= level_population
        return self.levels

    def generate_weights_for_nodes(self):
        weighted_nodes = {}
        for node in self.nodes:
            weighted_nodes.update({node: randint(1, 9)})
        return weighted_nodes

    def thin_out_edges(self, level):
        curr_length = len(self.levels[level])
        next_length = len(self.levels[level + 1])
        if curr_length > 1 and next_length > 1:
            for edge in range(max(curr_length, next_length)):
                try:
                    src = choice(self.levels[level])
                    dst = choice(self.levels[level + 1])
                    src_count = sum([self.edges.count((src, j)) for j in range(10)])
                    dst_count = sum([self.edges.count((j, dst)) for j in range(10)])
                    counter = randint(1, 3)
                    while src_count > counter and dst_count > counter:
                        self.edges.remove((src, dst))
                    else:
                        continue
                except ValueError:
                    continue

    def generate_edges(self):
        for level in range(len(self.levels) - 1):
            for node in self.levels[level]:
                targets = self.levels[level + 1][:]
                self.edges.extend([(node, target) for target in targets])
            self.thin_out_edges(level)
        return self.edges

    def generate_weights_for_edges(self):
        weighted_edges = {}
        for edge in self.edges:
            weighted_edges.update({edge: randint(1, 9)})
        return weighted_edges

    def generate_graph(self):
        self.generate_nodes()
        self.generate_edges()
        return self.nodes, self.edges, self.levels

    def generate_weighted_graph(self):
        self.generate_nodes()
        self.generate_edges()
        weighted_nodes = self.generate_weights_for_nodes()
        weighted_edges = self.generate_weights_for_edges()
        return self.nodes, self.edges, self.levels, weighted_nodes, weighted_edges

    def convert_to_matrix(self):
        matrix = [[0 for _ in range(self.number_nodes)] for _ in range(self.number_nodes)]
        for edge in self.edges:
            matrix[edge[0]][edge[1]] = 1
        return matrix


n = 15
graph = Graph(n)
nodes, edges, levels, weighted_nodes, weighted_edges = graph.generate_weighted_graph()


def build_graph():
    node_labels = {}
    g = nx.DiGraph()
    x, y, width = 0, -1, max([len(level) for level in levels])
    for node, weight in weighted_nodes.items():
        for level in range(len(levels)):
            if node in levels[level]:
                if x == -level:
                    y += 1
                else:
                    x = -level
                    y = width // 2 - len(levels[level]) // 2
                break
        g.add_node(node, pos=(y, x))
        node_labels[node] = weight
    for edge, weight in weighted_edges.items():
        g.add_edge(*edge, weight=weight)
    edge_labels = nx.get_edge_attributes(g, 'weight')
    pos = nx.get_node_attributes(g, 'pos')
    nx.draw(g, pos)
    nx.draw_networkx_labels(g, pos, node_labels, font_size=16)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
    plt.show()


def build_gantt_chart(data, time):
    fig, ax = plt.subplots()
    ax.set_ylim(5, len(data) * 15 + 10)
    ax.set_xlim(0, time + 5)
    ax.set_xlabel('seconds since start')
    ax.set_ylabel('processor\'s number')
    ax.set_yticks([i + 5 for i in range(10, n * 15, 15)])
    ax.set_yticklabels([str(i) for i in range(n)])
    ax.grid(True)
    for proc, params in data.items():
        ax.broken_barh([(params['start'], params['duration'])], (proc * 15 + 10, 10), facecolors='blue')

    plt.text(5, len(data) * 15 - 12, 'max time = {}'.format(time), fontsize=14)
    plt.show()


def min_time(curr_lvl, target):
    curr_min = 99999
    curr_node = None
    for node in curr_lvl:
        if weighted_edges.get((node, target)):
            if curr_lvl[node]['duration'] + weighted_edges[(node, target)] < curr_min:
                curr_min = curr_lvl[node]['duration'] + weighted_edges[(node, target)]
                curr_node = node
    return curr_node


def schedule_tasks():
    procs = {}
    for proc in range(n):
        procs.update({proc: {'start': 0, 'duration': weighted_nodes[proc]}})
    for level in range(len(levels) - 1):
        for target in levels[level + 1]:
            curr_node = min_time(procs, target)
            procs[curr_node]['duration'] += weighted_edges[(curr_node, target)]
            procs[target]['start'] = procs[curr_node]['duration']
            procs[target]['duration'] += procs[target]['start']
    time = 0
    for proc in procs:
        procs[proc]['duration'] = weighted_nodes[proc]
        this_time = procs[proc]['start'] + procs[proc]['duration']
        if this_time > time:
            time = this_time
    return procs, time


if __name__ == '__main__':
    build_graph()
    print(levels)
    print(weighted_nodes)
    print(weighted_edges)
    schedule, max_time = schedule_tasks()
    build_gantt_chart(schedule, max_time)

