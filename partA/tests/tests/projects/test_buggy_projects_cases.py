import requests
from pathlib import Path
import sys

# Add parent directory to path to import test_helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    PROJECTS,
    CATEGORIES,
    todo_server,
    generate_title,
    create_project,
    create_todo,
    create_category,
    require_created_id,
)

# Bug: Relation GET returns unrelated entity on invalid id

def test_bug_invalid_project_relation_get_returns_any_entity(todo_server):
    """BUG: GET /projects/:id/tasks returns unrelated todo for invalid id."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    payload = {"id": todo_id}
    _ = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)

    r = requests.get(f"{HOST}{PROJECTS}/0/tasks", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("todos")


def test_expected_invalid_project_relation_get_returns_404(todo_server):
    """EXPECTED: GET /projects/:id/tasks with invalid id returns 404."""
    r = requests.get(f"{HOST}{PROJECTS}/0/tasks", timeout=3)
    assert r.status_code == 404

# Bug: Relation POST with XML fails

def test_bug_post_project_tasks_xml_returns_404(todo_server):
    """BUG: POST /projects/:id/tasks with XML returns 404."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    xml_payload = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<todo>
    <id>{todo_id}</id>
</todo>"""

    r = requests.post(
        f"{HOST}{PROJECTS}/{project_id}/tasks",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3,
    )
    assert r.status_code == 404


def test_expected_post_project_tasks_xml_creates_relation(todo_server):
    """EXPECTED: POST /projects/:id/tasks with XML creates relation."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    xml_payload = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<todo>
    <id>{todo_id}</id>
</todo>"""

    r = requests.post(
        f"{HOST}{PROJECTS}/{project_id}/tasks",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3,
    )
    assert r.status_code == 201

# Bug: POST /projects skips id after invalid field

def test_bug_post_project_skips_id_after_invalid_field(todo_server):
    """BUG: POST /projects skips id after invalid payload."""
    first_resp = create_project()
    first_id = int(require_created_id(first_resp))

    invalid_payload = {"title": generate_title("invalid"), "invalidField": "x"}
    _ = requests.post(f"{HOST}{PROJECTS}", json=invalid_payload, timeout=3)

    second_resp = create_project()
    second_id = int(require_created_id(second_resp))
    assert second_id == first_id + 2


def test_expected_post_project_does_not_skip_id_after_invalid_field(todo_server):
    """EXPECTED: POST /projects does not skip id after invalid payload."""
    first_resp = create_project()
    first_id = int(require_created_id(first_resp))

    invalid_payload = {"title": generate_title("invalid"), "invalidField": "x"}
    _ = requests.post(f"{HOST}{PROJECTS}", json=invalid_payload, timeout=3)

    second_resp = create_project()
    second_id = int(require_created_id(second_resp))
    assert second_id == first_id + 1

# Bug: Secondary relation endpoints return 404 instead of 405

def test_bug_get_secondary_project_relation_returns_404(todo_server):
    """BUG: GET /projects/:id/tasks/:id returns 404 with empty body."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks/0", timeout=3)
    assert r.status_code == 404
    assert r.text.strip() == ""


def test_expected_get_secondary_project_relation_returns_405(todo_server):
    """EXPECTED: GET /projects/:id/tasks/:id returns 405."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks/0", timeout=3)
    assert r.status_code == 405


def test_bug_post_secondary_project_relation_returns_404(todo_server):
    """BUG: POST /projects/:id/tasks/:id returns 404 with empty body."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks/0", json={}, timeout=3)
    assert r.status_code == 404
    assert r.text.strip() == ""


def test_expected_post_secondary_project_relation_returns_405(todo_server):
    """EXPECTED: POST /projects/:id/tasks/:id returns 405."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks/0", json={}, timeout=3)
    assert r.status_code == 405

# Bug: URL parameter filters ignored on /projects/:id

def test_bug_get_project_by_id_ignores_query_filter(todo_server):
    """BUG: GET /projects/:id ignores query filters and returns project."""
    create_project_resp = create_project(name=generate_title("filter-bug"))
    project_id = require_created_id(create_project_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}?title=does-not-match", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("projects")


def test_expected_get_project_by_id_respects_query_filter(todo_server):
    """EXPECTED: GET /projects/:id respects query filters."""
    create_project_resp = create_project(name=generate_title("filter-exp"))
    project_id = require_created_id(create_project_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}?title=does-not-match", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("projects") == []

# Bug: POST /projects/:id/tasks creates todo without id

def test_bug_post_project_tasks_without_id_creates_todo(todo_server):
    """BUG: POST /projects/:id/tasks creates a new todo when id missing."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    payload = {"title": generate_title("created-by-bug")}
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)
    assert r.status_code == 201

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert any(t.get("title") == payload["title"] for t in body.get("todos", []))


def test_expected_post_project_tasks_without_id_returns_400(todo_server):
    """EXPECTED: POST /projects/:id/tasks without id returns 400."""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    payload = {"title": generate_title("missing-id")}
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)
    assert r.status_code == 400

# Bug: Undocumented relation collection endpoints

def test_bug_get_projects_categories_returns_all(todo_server):
    """BUG: GET /projects/categories returns all categories."""
    create_category_resp = create_category()
    _ = require_created_id(create_category_resp)

    r = requests.get(f"{HOST}{PROJECTS}/categories", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("categories")


def test_expected_get_projects_categories_returns_404(todo_server):
    """EXPECTED: GET /projects/categories returns 404."""
    r = requests.get(f"{HOST}{PROJECTS}/categories", timeout=3)
    assert r.status_code == 404


def test_bug_delete_projects_categories_deletes_category(todo_server):
    """BUG: DELETE /projects/categories deletes category specified in body."""
    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    r = requests.delete(
        f"{HOST}{PROJECTS}/categories",
        json={"id": category_id},
        timeout=3,
    )
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{CATEGORIES}/{category_id}", timeout=3)
    assert r2.status_code == 404


def test_expected_delete_projects_categories_returns_404(todo_server):
    """EXPECTED: DELETE /projects/categories returns 404."""
    r = requests.delete(f"{HOST}{PROJECTS}/categories", timeout=3)
    assert r.status_code == 404
