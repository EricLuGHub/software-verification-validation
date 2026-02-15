import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    TODOS,
    CATEGORIES,
    todo_server,
    generate_title,
    create_todo,
    create_category,
    require_created_id,
)

# Bug: Relation GET returns unrelated entity on invalid id

def test_bug_invalid_todo_relation_get_returns_any_entity(todo_server):
    """BUG: GET /todos/:id/categories returns unrelated category for invalid id."""
    create_category_resp = create_category(name=generate_title("cat-bug"))
    category_id = require_created_id(create_category_resp)

    create_todo_resp = create_todo(categories=[{"id": category_id}])
    _ = require_created_id(create_todo_resp)

    r = requests.get(f"{HOST}{TODOS}/0/categories", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("categories")


def test_expected_invalid_todo_relation_get_returns_404(todo_server):
    """EXPECTED: GET /todos/:id/categories with invalid id returns 404."""
    r = requests.get(f"{HOST}{TODOS}/0/categories", timeout=3)
    assert r.status_code == 404

# Bug: Relation POST with XML fails

def test_bug_post_todo_categories_xml_returns_404(todo_server):
    """BUG: POST /todos/:id/categories with XML returns 404."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    xml_payload = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<category>
    <id>{category_id}</id>
</category>"""

    r = requests.post(
        f"{HOST}{TODOS}/{todo_id}/categories",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3,
    )
    assert r.status_code == 404


def test_expected_post_todo_categories_xml_creates_relation(todo_server):
    """EXPECTED: POST /todos/:id/categories with XML creates relation."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    xml_payload = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<category>
    <id>{category_id}</id>
</category>"""

    r = requests.post(
        f"{HOST}{TODOS}/{todo_id}/categories",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3,
    )
    assert r.status_code == 201

# Bug: POST /todos skips id after invalid field

def test_bug_post_todo_skips_id_after_invalid_field(todo_server):
    """BUG: POST /todos skips id after invalid payload."""
    first_resp = create_todo()
    first_id = int(require_created_id(first_resp))

    invalid_payload = {"title": generate_title("invalid"), "invalidField": "x"}
    _ = requests.post(f"{HOST}{TODOS}", json=invalid_payload, timeout=3)

    second_resp = create_todo()
    second_id = int(require_created_id(second_resp))
    assert second_id == first_id + 2


def test_expected_post_todo_does_not_skip_id_after_invalid_field(todo_server):
    """EXPECTED: POST /todos does not skip id after invalid payload."""
    first_resp = create_todo()
    first_id = int(require_created_id(first_resp))

    invalid_payload = {"title": generate_title("invalid"), "invalidField": "x"}
    _ = requests.post(f"{HOST}{TODOS}", json=invalid_payload, timeout=3)

    second_resp = create_todo()
    second_id = int(require_created_id(second_resp))
    assert second_id == first_id + 1

# Bug: Secondary relation endpoints return 404 instead of 405

def test_bug_get_secondary_todo_relation_returns_404(todo_server):
    """BUG: GET /todos/:id/tasksof/:id returns 404 with empty body."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof/0", timeout=3)
    assert r.status_code == 404
    assert r.text.strip() == ""


def test_expected_get_secondary_todo_relation_returns_405(todo_server):
    """EXPECTED: GET /todos/:id/tasksof/:id returns 405."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof/0", timeout=3)
    assert r.status_code == 405


def test_bug_post_secondary_todo_relation_returns_404(todo_server):
    """BUG: POST /todos/:id/tasksof/:id returns 404 with empty body."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    r = requests.post(f"{HOST}{TODOS}/{todo_id}/tasksof/0", json={}, timeout=3)
    assert r.status_code == 404
    assert r.text.strip() == ""


def test_expected_post_secondary_todo_relation_returns_405(todo_server):
    """EXPECTED: POST /todos/:id/tasksof/:id returns 405."""
    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    r = requests.post(f"{HOST}{TODOS}/{todo_id}/tasksof/0", json={}, timeout=3)
    assert r.status_code == 405

# Bug: URL parameter filters ignored on /todos/:id

def test_bug_get_todo_by_id_ignores_query_filter(todo_server):
    """BUG: GET /todos/:id ignores query filters and returns todo."""
    create_todo_resp = create_todo(title=generate_title("filter-bug"))
    todo_id = require_created_id(create_todo_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}?title=does-not-match", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("todos")


def test_expected_get_todo_by_id_respects_query_filter(todo_server):
    """EXPECTED: GET /todos/:id respects query filters."""
    create_todo_resp = create_todo(title=generate_title("filter-exp"))
    todo_id = require_created_id(create_todo_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}?title=does-not-match", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("todos") == []

# Bug: /todos/tasks unsupported endpoints return 400

def test_bug_get_todos_tasks_returns_400(todo_server):
    """BUG: GET /todos/tasks returns 400 with index error message."""
    r = requests.get(f"{HOST}{TODOS}/tasks", timeout=3)
    assert r.status_code == 400
    assert "Index 0 out of bounds" in r.text


def test_expected_get_todos_tasks_returns_404(todo_server):
    """EXPECTED: GET /todos/tasks returns 404."""
    r = requests.get(f"{HOST}{TODOS}/tasks", timeout=3)
    assert r.status_code == 404


def test_bug_delete_todos_tasks_returns_400(todo_server):
    """BUG: DELETE /todos/tasks returns 400 with index error message."""
    r = requests.delete(f"{HOST}{TODOS}/tasks", timeout=3)
    assert r.status_code == 400
    assert "Index 0 out of bounds" in r.text


def test_expected_delete_todos_tasks_returns_404(todo_server):
    """EXPECTED: DELETE /todos/tasks returns 404."""
    r = requests.delete(f"{HOST}{TODOS}/tasks", timeout=3)
    assert r.status_code == 404

# Bug: Undocumented relation collection endpoints

def test_bug_get_todos_categories_returns_all(todo_server):
    """BUG: GET /todos/categories returns all categories."""
    create_category_resp = create_category()
    _ = require_created_id(create_category_resp)

    r = requests.get(f"{HOST}{TODOS}/categories", timeout=3)
    assert r.status_code == 200
    body = r.json()
    assert body.get("categories")


def test_expected_get_todos_categories_returns_404(todo_server):
    """EXPECTED: GET /todos/categories returns 404."""
    r = requests.get(f"{HOST}{TODOS}/categories", timeout=3)
    assert r.status_code == 404
