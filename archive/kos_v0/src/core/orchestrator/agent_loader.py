from src.core.klf.node_loader import load_all_nodes

def load_agents():
    print("[ORCH] Loading 13 node classes via KLF...")
    nodes = load_all_nodes()
    for name in nodes:
        print(f"[ORCH] Loaded: {name} -> {type(nodes[name]).__name__}")
    return nodes
