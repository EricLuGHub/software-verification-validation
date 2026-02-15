import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    TODOS,
    todo_server,
    assert_has_common_headers,
    generate_title,
    create_todo,
    require_created_id,
    assert_subset,
    todos_contain_expected,
)


def test_create_todo(todo_server):
    """POST /todos creates a new todo with title."""
    title = generate_title("create")
    r = create_todo(title=title)
    assert r.status_code == 201
    body = r.json()
    expected = {
        "id": str(int(body.get("id", "0"))),  
        "title": title,
        "doneStatus": "false",
        "description": ""
    }
    assert_subset(expected, body)


def test_get_todo_by_id_existing(todo_server):
    """GET /todos/:id returns the specific todo."""
    title = generate_title("get-by-id")
    create_resp = create_todo(title=title)

    todo_id = require_created_id(create_resp)
    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=2)

    assert r.status_code == 200
    body = r.json()

    expected = {
        "todos": [
            {
                "id": str(int(todo_id)),
                "title": title,
                "doneStatus": "false",
                "description": "",

            }
        ]
    }

    assert_subset(expected, body)


def test_get_todo_by_id_filter(todo_server):
    """GET /todos/:id?id=X filters by query parameter."""
    title = generate_title("get-by-id")
    create_resp = create_todo(title=title)

    todo_id = require_created_id(create_resp)
    r = requests.get(f"{HOST}{TODOS}/{todo_id}?id={todo_id}", timeout=2)

    assert r.status_code == 200
    body = r.json()

    expected = {
        "todos": [
            {
                "title": title,
                "doneStatus": "false",
                "description": ""
            }
        ]
    }

    assert_subset(expected, body)


def test_get_todos_returns_all(todo_server):
    """GET /todos returns all created todos."""
    todo1_title = generate_title("get-all-1")
    todo2_title = generate_title("get-all-2")

    create_resp1 = create_todo(title=todo1_title)
    create_resp2 = create_todo(title=todo2_title)
    todo1_id = require_created_id(create_resp1)
    todo2_id = require_created_id(create_resp2)

    r = requests.get(f"{HOST}{TODOS}", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected_todo1 = {
        "id": str(int(todo1_id)),
        "title": todo1_title,
        "doneStatus": "false",
        "description": ""
    }

    expected_todo2 = {
        "id": str(int(todo2_id)),
        "title": todo2_title,
        "doneStatus": "false",
        "description": ""
    }

    todos_contain_expected(body, [expected_todo1, expected_todo2])


def test_head_todos_returns_headers(todo_server):
    """HEAD /todos returns headers only."""
    r = requests.head(f"{HOST}{TODOS}", timeout=3)
    assert r.status_code in (200, 204)
    assert_has_common_headers(r)


def test_get_todos_filter_by_title_query_param(todo_server):
    """GET /todos?title=X filters by title query parameter."""
    title = generate_title("query-param")
    create_resp = create_todo(title=title)
    todo_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{TODOS}?title={requests.utils.quote(title)}", timeout=3)
    assert r.status_code == 200
    body = r.json()
    expected = {
        "todos": [
            {
                "id": str(int(todo_id)),
                "title": title,
                "doneStatus": "false",
                "description": ""
            }
        ]
    }
    assert_subset(expected, body)


def test_get_todo_by_id_existing(todo_server):
    """GET /todos/:id verifies todo exists."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r.status_code == 200
    _ = r.json()


def test_head_todo_by_id_headers(todo_server):
    """HEAD /todos/:id returns headers only."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r.status_code == 200
    assert_has_common_headers(r)


def test_post_todo_by_id_amends_title(todo_server):
    """POST /todos/:id updates todo title."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-post"),
    }
    r = requests.post(f"{HOST}{TODOS}/{todo_id}", json=payload, timeout=3)
    assert r.status_code in (200, 204)

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"][0]["title"] == payload["title"]


def test_post_todo_by_id_amends_doneStatus(todo_server):
    """POST /todos/:id updates todo doneStatus."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    payload = {
        "doneStatus": True,
    }
    r = requests.post(f"{HOST}{TODOS}/{todo_id}", json=payload, timeout=3)
    assert r.status_code in (200, 204)

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"][0]["doneStatus"] == "true"


def test_post_todo_by_id_amends_description(todo_server):
    """POST /todos/:id updates todo description."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    payload = {
        "description": generate_title("amend-post-desc"),
    }
    r = requests.post(f"{HOST}{TODOS}/{todo_id}", json=payload, timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"][0]["description"] == payload["description"]


def test_post_todo_by_id_amends_multiple_fields(todo_server):
    """POST /todos/:id updates multiple todo fields."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-post-multi"),
        "doneStatus": True,
        "description": generate_title("amend-post-multi-desc")
    }
    r = requests.post(f"{HOST}{TODOS}/{todo_id}", json=payload, timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"][0]["title"] == payload["title"]
    assert body["todos"][0]["doneStatus"] == "true"
    assert body["todos"][0]["description"] == payload["description"]


def test_delete_todo_by_id_deletes(todo_server):
    """DELETE /todos/:id removes the todo."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.delete(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 404


# XML Format Tests

def test_create_todo_xml(todo_server):
    """POST /todos with XML content type creates a new todo."""
    title = generate_title("create-todo-xml")
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<todo>
    <title>{title}</title>
    <doneStatus>false</doneStatus>
    <description></description>
</todo>"""
    
    r = requests.post(
        f"{HOST}{TODOS}",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3
    )
    assert r.status_code == 201


def test_get_todo_xml_accept(todo_server):
    """GET /todos/:id with Accept: application/xml returns XML response."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)
    
    r = requests.get(
        f"{HOST}{TODOS}/{todo_id}",
        headers={"Accept": "application/xml"},
        timeout=3
    )
    assert r.status_code == 200
    assert "application/xml" in r.headers.get("Content-Type", "")


def test_get_all_todos_xml(todo_server):
    """GET /todos with Accept: application/xml returns all todos in XML."""
    title = generate_title("get-all-xml")
    create_todo(title=title)
    
    r = requests.get(
        f"{HOST}{TODOS}",
        headers={"Accept": "application/xml"},
        timeout=3
    )
    assert r.status_code == 200
    assert "application/xml" in r.headers.get("Content-Type", "")


def test_post_todo_xml_update(todo_server):
    """POST /todos/:id with XML updates todo."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)
    
    new_title = generate_title("updated-xml")
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<todo>
    <title>{new_title}</title>
</todo>"""
    
    r = requests.post(
        f"{HOST}{TODOS}/{todo_id}",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3
    )
    assert r.status_code == 200
    
    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["todos"][0]["title"] == new_title
