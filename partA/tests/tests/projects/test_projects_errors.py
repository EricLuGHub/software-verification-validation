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
    generate_title,
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


def test_get_projects_filter_by_id_nonexistent(todo_server):
    """GET /projects?id=0 with nonexistent ID returns empty list."""
    r = requests.get(f"{HOST}{PROJECTS}?id=0", timeout=3)
    assert r.status_code == 200
    body = r.json()
    
    assert body["projects"] == []


def test_post_project_with_invalid_field(todo_server):
    """POST /projects with invalid field returns error."""
    payload = {
        "title": generate_title("project"),
        "invalidField": "test"
    }
    r = requests.post(f"{HOST}{PROJECTS}", json=payload, timeout=3)
    assert r.status_code == 400
    
    body = r.json()
    assert "errorMessages" in body
    assert "Could not find field: invalidField" in str(body["errorMessages"])


def test_post_project_with_id_in_payload(todo_server):
    """POST /projects with id in payload returns error."""
    payload = {
        "id": "999",
        "title": generate_title("project"),
        "description": "test"
    }
    r = requests.post(f"{HOST}{PROJECTS}", json=payload, timeout=3)
    assert r.status_code == 400
    
    body = r.json()
    assert "errorMessages" in body


def test_put_project_by_id_with_invalid_field(todo_server):
    """PUT /projects/:id with invalid field returns 400."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-project"),
        "invalidField": "test"
    }
    r = requests.put(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 400


def test_put_project_nonexistent_id(todo_server):
    """PUT /projects/0 with nonexistent ID returns 404."""
    payload = {
        "title": generate_title("amend-project"),
        "description": "test"
    }
    r = requests.put(f"{HOST}{PROJECTS}/0", json=payload, timeout=3)
    assert r.status_code == 404


def test_get_project_with_blank_id(todo_server):
    """GET /projects/ with trailing slash but no ID."""
    r = requests.get(f"{HOST}{PROJECTS}/", timeout=3)
    
    # Document behavior
    assert r.status_code in (200, 404)
