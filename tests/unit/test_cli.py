import os
import json
from argparse import Namespace
from stancectl.cli import cmd_init


def test_init_creates_file_in_cwd(tmp_path, monkeypatch):
    """
    Proves that stancectl init writes package.json to the caller's
    working directory, not the CLI's installation directory.
    """
    # Simulate being in a temporary directory
    monkeypatch.chdir(tmp_path)

    args = Namespace(package_id="org.example.test")

    # Run the init command
    cmd_init(args)

    # Assert package.json was created exactly in our current working directory
    expected_path = tmp_path / "package.json"
    assert expected_path.exists(), (
        "package.json should be created in the caller's working directory"
    )

    # Verify the contents
    with open(expected_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["packageId"] == "org.example.test"
