import json
import os
from jsonschema import validate, ValidationError
from typing import Dict, List, Any, Optional


def load_schema() -> Dict[str, Any]:
    # Locate schema relative to the project root
    # Since this runs from Source/tools/stancectl/stancectl or via direnv
    # we can find the schema in Source/schemas/stance-package.schema.json
    # or rely on an environment variable or relative paths.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # stancectl/stancectl -> tools/stancectl -> tools -> Source
    source_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    schema_path = os.path.join(source_dir, "schemas", "stance-package.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


class StanceValidationError(Exception):
    pass


class Diagnostic:
    def __init__(self, level: str, message: str, path: Optional[str] = None):
        self.level = level
        self.message = message
        self.path = path

    def to_dict(self):
        res = {"level": self.level, "message": self.message}
        if self.path:
            res["path"] = self.path
        return res


class Validator:
    def __init__(self):
        self.schema = load_schema()
        self.diagnostics: List[Diagnostic] = []

    def add_error(self, message: str, path: str = None):
        self.diagnostics.append(Diagnostic("error", message, path))

    def validate_package(self, package_data: Dict[str, Any]) -> bool:
        self.diagnostics.clear()

        # 1. JSON Schema validation
        try:
            validate(instance=package_data, schema=self.schema)
        except ValidationError as e:
            path_str = ".".join(str(p) for p in e.path)
            self.add_error(f"Schema validation failed: {e.message}", path_str)
            return False

        package_id = package_data.get("packageId")

        # 2. Semantic validation
        trees = package_data.get("trees", [])
        tree_ids = set()

        for tree_idx, tree in enumerate(trees):
            tree_id = tree.get("treeId")
            tree_path = f"trees[{tree_idx}]"

            if tree_id in tree_ids:
                self.add_error(f"Duplicate treeId '{tree_id}'", tree_path)
            tree_ids.add(tree_id)

            self._validate_tree(tree, tree_path, package_id)

        return len(self.diagnostics) == 0

    def _validate_tree(self, tree: Dict[str, Any], path: str, package_id: str):
        tree_id = tree.get("treeId")
        default_node = tree.get("defaultNode")
        nodes = tree.get("nodes", [])

        node_map = {}
        for node_idx, node in enumerate(nodes):
            node_id = node.get("nodeId")
            node_path = f"{path}.nodes[{node_idx}]"

            if node_id in node_map:
                self.add_error(
                    f"Duplicate nodeId '{node_id}' in tree '{tree_id}'", node_path
                )
            else:
                node_map[node_id] = node

        # Validate defaultNode exists
        if default_node and default_node not in node_map:
            self.add_error(
                f"defaultNode '{default_node}' not found in tree '{tree_id}'", path
            )

        # Validate parents and cycles
        for node_id, node in node_map.items():
            parent_id = node.get("parent")
            node_path = f"{path}.nodes[{nodes.index(node)}]"

            if parent_id is not None:
                if parent_id not in node_map:
                    self.add_error(
                        f"Parent '{parent_id}' for node '{node_id}' does not exist in tree '{tree_id}'",
                        node_path,
                    )

            # Cycle detection
            visited = set()
            current_id = node_id
            cycle_found = False

            while current_id is not None:
                if current_id in visited:
                    cycle_found = True
                    break
                visited.add(current_id)

                curr_node = node_map.get(current_id)
                if curr_node:
                    current_id = curr_node.get("parent")
                else:
                    break

            if cycle_found:
                self.add_error(
                    f"Cycle detected in parent chain for node '{node_id}'", node_path
                )
