import requests
from pathlib import Path
import sys

# Add parent directory to path to import test_helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    PROJECTS,
    todo_server,
    assert_has_common_headers,
    generate_title,
    create_project,
    create_todo,
    create_category,
    require_created_id,
    assert_subset,
)


def test_get_project_tasks_no_link(todo_server):
    """GET /projects/:id/tasks returns empty list when no tasks linked."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r.status_code == 200
    body = r.json()

    assert r.status_code == 200
    assert "todos" in body
    assert isinstance(body["todos"], list)
    assert body["todos"] == []


def test_get_project_tasks(todo_server):
    """GET /projects/:id/tasks returns all linked todos."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    payload = {"id": todo_id}
    r_rel = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)
    assert r_rel.status_code == 201  

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected = {
        "todos": [
            {"id": todo_id},
        ]
    }
    assert_subset(expected, body)


def test_head_project_tasks(todo_server):
    """HEAD /projects/:id/tasks returns headers only."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r.status_code == 200
    if r.status_code == 200:
        assert_has_common_headers(r)


def test_post_project_tasks_creates_relationship(todo_server):
    """POST /projects/:id/tasks creates project-todo relationship."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    payload = {"id": todo_id}
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)
    assert r.status_code == 201  

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"][0]["id"] == todo_id


def test_delete_project_task_relationship(todo_server):
    """DELETE /projects/:id/tasks/:id removes the relationship."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    payload = {"id": todo_id}
    _ = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)

    r = requests.delete(f"{HOST}{PROJECTS}/{project_id}/tasks/{todo_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"] == []


def test_get_project_categories_no_link(todo_server):
    """GET /projects/:id/categories returns empty list when no categories linked."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/categories", timeout=3)
    assert r.status_code == 200
    body = r.json()

    assert r.status_code == 200
    assert "categories" in body
    assert isinstance(body["categories"], list)
    assert body["categories"] == []


def test_get_project_categories(todo_server):
    """GET /projects/:id/categories returns all linked categories."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    payload = {"id": category_id}
    r_rel = requests.post(f"{HOST}{PROJECTS}/{project_id}/categories", json=payload, timeout=3)
    assert r_rel.status_code == 201

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/categories", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected = {
        "categories": [
            {"id": category_id},
        ]
    }
    assert_subset(expected, body)


def test_head_project_categories(todo_server):
    """HEAD /projects/:id/categories returns headers only."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/categories", timeout=3)
    assert r.status_code == 200
    if r.status_code == 200:
        assert_has_common_headers(r)


def test_post_project_categories_creates_relationship(todo_server):
    """POST /projects/:id/categories creates project-category relationship."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    payload = {"id": category_id}
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/categories", json=payload, timeout=3)
    assert r.status_code == 201

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}/categories", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["categories"][0]["id"] == category_id


def test_delete_project_category_relationship(todo_server):
    """DELETE /projects/:id/categories/:id removes the relationship."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    payload = {"id": category_id}
    _ = requests.post(f"{HOST}{PROJECTS}/{project_id}/categories", json=payload, timeout=3)

    r = requests.delete(f"{HOST}{PROJECTS}/{project_id}/categories/{category_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}/categories", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["categories"] == []
