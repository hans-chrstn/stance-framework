import pytest
from stancectl.validator import Validator


@pytest.fixture
def base_package():
    return {
        "schemaVersion": 1,
        "packageId": "test.package",
        "packageVersion": "0.1.0",
        "displayName": "Test Package",
        "trees": [
            {
                "treeId": "main",
                "displayName": "Main",
                "defaultNode": "root",
                "nodes": [
                    {
                        "nodeId": "root",
                        "displayName": "Root",
                        "parent": None,
                        "order": 0,
                        "unlock": {"mode": "always"},
                    }
                ],
            }
        ],
    }


def test_valid_package(base_package):
    validator = Validator()
    assert validator.validate_package(base_package) is True
    assert len(validator.diagnostics) == 0


def test_missing_parent(base_package):
    base_package["trees"][0]["nodes"].append(
        {
            "nodeId": "child",
            "displayName": "Child",
            "parent": "nonexistent",
            "order": 1,
            "unlock": {"mode": "always"},
        }
    )
    validator = Validator()
    assert validator.validate_package(base_package) is False
    assert any("does not exist in tree" in d.message for d in validator.diagnostics)


def test_duplicate_node_id(base_package):
    base_package["trees"][0]["nodes"].append(
        {
            "nodeId": "root",
            "displayName": "Another Root",
            "parent": None,
            "order": 1,
            "unlock": {"mode": "always"},
        }
    )
    validator = Validator()
    assert validator.validate_package(base_package) is False
    assert any("Duplicate nodeId 'root'" in d.message for d in validator.diagnostics)


def test_cycle_detection(base_package):
    # A -> B -> C -> A
    base_package["trees"][0]["nodes"] = [
        {
            "nodeId": "a",
            "displayName": "A",
            "parent": "c",
            "order": 0,
            "unlock": {"mode": "always"},
        },
        {
            "nodeId": "b",
            "displayName": "B",
            "parent": "a",
            "order": 1,
            "unlock": {"mode": "always"},
        },
        {
            "nodeId": "c",
            "displayName": "C",
            "parent": "b",
            "order": 2,
            "unlock": {"mode": "always"},
        },
    ]
    base_package["trees"][0]["defaultNode"] = "a"
    validator = Validator()
    assert validator.validate_package(base_package) is False
    assert any("Cycle detected" in d.message for d in validator.diagnostics)


def test_invalid_schema(base_package):
    del base_package["packageId"]
    validator = Validator()
    assert validator.validate_package(base_package) is False
    assert any("Schema validation failed" in d.message for d in validator.diagnostics)
