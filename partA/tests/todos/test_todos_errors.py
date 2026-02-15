import requests
from pathlib import Path
import sys

# Add parent directory to path to import test_helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    TODOS,
    todo_server,
    assert_subset,
    require_created_id,
    create_todo,
)


def test_get_todo_by_id_nonexistent(todo_server):
    """GET /todos/0 returns 404 for nonexistent todo."""
    todo_id = 0
    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=2)
    expected = {
        "errorMessages": [
            "Could not find an instance with todos/0"
        ]
    }

    assert r.status_code == 404
    assert_subset(expected, r.json())


def test_get_todo_by_id_invalid(todo_server):
    """GET /todos/abc returns 404 for invalid todo ID."""
    todo_id = "abc"
    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=2)
    expected = {
        "errorMessages": [
            "Could not find an instance with todos/abc"
        ]
    }
    assert r.status_code == 404
    assert_subset(expected, r.json())


def test_get_todo_by_id_nonexistent_with_id_query(todo_server):
    """GET /todos?id=0 returns empty list for nonexistent todo."""
    todo_id = 0
    r = requests.get(f"{HOST}{TODOS}?id={todo_id}", timeout=2)
    expected = {
        "todos": []
    }

    assert r.status_code == 200
    assert_subset(expected, r.json())


def test_get_todo_filter_by_id_query_nonexistant_param(todo_server):
    """GET /todos?id=0 returns empty list with nonexistent ID."""
    r = requests.get(f"{HOST}{TODOS}?id=0", timeout=3)
    assert r.status_code == 200
    body = r.json()
    expected = {
        "todos": []
    }
    assert_subset(expected, body)


def test_post_todo_not_valid_field(todo_server):
    """POST /todos/:id with invalid field returns 400."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    payload = {
        "errorMessages": [
            "Could not find field: notvalid"
        ]
    }
    r = requests.post(f"{HOST}{TODOS}/{todo_id}", json=payload, timeout=3)
    assert r.status_code == 400


def test_delete_todo_by_id_nonexistent(todo_server):
    """DELETE /todos/0 returns 404 for nonexistent todo."""
    r = requests.delete(f"{HOST}{TODOS}/0", timeout=3)
    assert r.status_code == 404
