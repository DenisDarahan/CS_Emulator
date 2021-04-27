from json import JSONEncoder

from .node import Node
from .edge import Edge


class Encoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, Node):
            return {'node_id': o.node_id, 'node_weight': o.weight, 'node_pos': o.node_pos}

        if isinstance(o, Edge):
            return {'edge_id': o.edge_id, 'edge_weight': o.weight, 'src_node_id': o.src_node.node_id,
                    'dst_node_id': o.dst_node.node_id}

        return JSONEncoder.default(self, o)
