class Node:

    def __init__(self, node_id: int, node_weight: int, node_pos: tuple):
        self.node_id = node_id
        self.weight = node_weight
        self.node_pos = node_pos

    def __str__(self):
        return f'Node {self.node_id} | Weight({self.weight}) | Pos({self.node_pos})'
