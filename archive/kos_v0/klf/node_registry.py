NODES = {}

def register_node(node_id, metadata):
    NODES[node_id] = metadata

def list_nodes():
    return NODES
