import json
from pathlib import Path
from copy import deepcopy

BB_PATH = Path(__file__).parent.parent / "blackboard.json"


class Blackboard:
    def __init__(self, path=BB_PATH):
        self.path = Path(path)
        with open(self.path) as f:
            self.data = json.load(f)

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, *keys):
        node = self.data
        for k in keys:
            node = node[k]
        return node

    def set(self, value, *keys):
        node = self.data
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] = value
        self._save()

    def update(self, d):
        def deep_merge(base, overlay):
            for k, v in overlay.items():
                if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                    deep_merge(base[k], v)
                else:
                    base[k] = v
        deep_merge(self.data, d)
        self._save()

    def increment(self, *keys):
        node = self.data
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] += 1
        self._save()
