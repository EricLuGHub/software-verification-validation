import requests
from pathlib import Path
import sys

# Add parent directory to path to import test_helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    PROJECTS,
    todo_server,
    assert_subset,
    require_created_id,
    create_project,
)


def test_get_project_by_id_nonexistent(todo_server):
    """GET /projects/0 returns 404 for nonexistent project."""
    project_id = 0
    r = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    expected = {
        "errorMessages": [
            f"Could not find an instance with projects/{project_id}"
        ]
    }
    assert r.status_code == 404
    assert_subset(expected, r.json())


def test_get_project_by_id_invalid(todo_server):
    """GET /projects/abc returns 404 for invalid project ID."""
    project_id = "abc"
    r = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    expected = {
        "errorMessages": [
            f"Could not find an instance with projects/{project_id}"
        ]
    }
    assert r.status_code == 404
    assert_subset(expected, r.json())


def test_get_project_by_id_nonexistent_with_id_query(todo_server):
    """GET /projects?id=0 returns empty list for nonexistent project."""
    project_id = 0
    r = requests.get(f"{HOST}{PROJECTS}?id={project_id}", timeout=3)
    expected = {"projects": []}
    assert r.status_code == 200
    assert_subset(expected, r.json())


def test_delete_project_by_id_nonexistent(todo_server):
    """DELETE /projects/0 returns 404 for nonexistent project."""
    r = requests.delete(f"{HOST}{PROJECTS}/0", timeout=3)
    assert r.status_code == 404
