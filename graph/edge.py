class Edge:

    def __init__(self, edge_id: int, edge_weight: int, src_node, dst_node):
        self.edge_id = edge_id
        self.weight = edge_weight
        self.src_node = src_node
        self.dst_node = dst_node

    def __str__(self):
        return (f'Edge {self.edge_id} | Weight({self.weight}) | '
                f'Src({self.src_node.node_id}) | Dst({self.dst_node.node_id})')
