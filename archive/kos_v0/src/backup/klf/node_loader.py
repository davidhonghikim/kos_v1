import importlib
from src.core.klf.node_manifest import NODE_CLASSES

def load_all_nodes():
    loaded = {}
    for name, path in NODE_CLASSES.items():
        module_path, class_name = path.rsplit(".", 1)
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        loaded[name] = cls()
    return loaded
