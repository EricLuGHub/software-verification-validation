import requests
from pathlib import Path
import sys

# Add parent directory to path to import test_helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    TODOS,
    CATEGORIES,
    PROJECTS,
    todo_server,
    assert_has_common_headers,
    generate_title,
    create_todo,
    create_category,
    create_project,
    require_created_id,
    assert_subset,
)


def test_get_todo_categories(todo_server):
    """GET /todos/:id/categories returns all linked categories."""
    new_category_name = generate_title("category")
    create_category_resp = create_category(name=new_category_name)
    assert create_category_resp.status_code == 201

    category_id = require_created_id(create_category_resp)

    create_resp = create_todo(categories=[{"id": category_id}])
    todo_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}/categories", timeout=3)
    body = r.json()

    assert r.status_code == 200

    expected = {
        "categories": [
            {"id": category_id},
        ]
    }

    assert_subset(expected, body)


def test_get_todo_categories_undocumented(todo_server):
    """GET /todos/categories returns all categories (undocumented endpoint)."""
    new_cat1 = generate_title("catkcat")
    create_category_resp1 = create_category(name=new_cat1)

    expected1 = {
        "id": require_created_id(create_category_resp1),
        "title": new_cat1,
        "description": ""
    }

    new_todo = generate_title("todo")
    create_resp = create_todo(title=new_todo, categories=[{"id": expected1["id"]}])
    assert create_resp.status_code == 201

    r = requests.get(f"{HOST}{TODOS}/categories", timeout=3)
    assert r.status_code == 200

    body = r.json()
    assert "categories" in body
    categories = body["categories"]
    assert expected1 in categories


def test_head_todo_categories(todo_server):
    """HEAD /todos/:id/categories returns headers only."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{TODOS}/{todo_id}/categories", timeout=3)
    assert r.status_code in (200, 204, 404)
    if r.status_code in (200, 204):
        assert_has_common_headers(r)


def test_post_todo_categories_creates_relationship(todo_server):
    """POST /todos/:id/categories creates todo-category relationship."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    new_category_name = generate_title("category")
    create_category_resp = create_category(name=new_category_name)
    assert create_category_resp.status_code == 201

    category_id = require_created_id(create_category_resp)
    payload = {"id": category_id}

    r = requests.post(f"{HOST}{TODOS}/{todo_id}/categories", json=payload, timeout=3)
    assert r.status_code == 201

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}/categories", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["categories"][0]["id"] == category_id


def test_delete_todo_category_relationship(todo_server):
    """DELETE /todos/:id/categories/:id removes the relationship."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    new_category_name = generate_title("category")
    create_category_resp = create_category(name=new_category_name)
    assert create_category_resp.status_code == 201

    category_id = require_created_id(create_category_resp)
    payload = {"id": category_id}
    _ = requests.post(f"{HOST}{TODOS}/{todo_id}/categories", json=payload, timeout=3)

    r = requests.delete(f"{HOST}{TODOS}/{todo_id}/categories/{category_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}/categories", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["categories"] == []


def test_get_todo_tasksof_no_link(todo_server):
    """GET /todos/:id/tasksof returns empty list when no projects linked."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r.status_code in (200, 404)
    body = r.json()

    assert r.status_code == 200
    assert "projects" in body
    assert isinstance(body["projects"], list)
    assert body["projects"] == []


def test_get_todo_tasksof(todo_server):
    """GET /todos/:id/tasksof returns all linked projects."""
    new_project_name = generate_title("project")
    create_project_resp = create_project(name=new_project_name)
    assert create_project_resp.status_code == 201
    project_id = require_created_id(create_project_resp)

    create_resp = create_todo(tasksof=[{"id": project_id}])
    todo_id = require_created_id(create_resp)

    payload = {"id": project_id}
    _ = requests.post(f"{HOST}{TODOS}/{todo_id}/tasksof", json=payload, timeout=3)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected = {
        "projects": [
            {"id": project_id},
        ]
    }

    assert_subset(expected, body)


def test_head_todo_tasksof(todo_server):
    """HEAD /todos/:id/tasksof returns headers only."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r.status_code in (200, 204, 404)
    if r.status_code in (200, 204):
        assert_has_common_headers(r)


def test_post_todo_tasksof_creates_relationship(todo_server):
    """POST /todos/:id/tasksof creates todo-project relationship."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    new_project_name = generate_title("project")
    create_project_resp = create_project(name=new_project_name)
    assert create_project_resp.status_code == 201

    project_id = require_created_id(create_project_resp)
    payload = {"id": project_id}

    r = requests.post(f"{HOST}{TODOS}/{todo_id}/tasksof", json=payload, timeout=3)
    assert r.status_code == 201

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r2.status_code == 200
    
    body = r2.json()
    assert body["projects"][0]["id"] == project_id


def test_delete_todo_tasksof_relationship(todo_server):
    """DELETE /todos/:id/tasksof/:id removes the relationship."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    new_project_name = generate_title("project")
    create_project_resp = create_project(name=new_project_name)
    assert create_project_resp.status_code == 201
    project_id = require_created_id(create_project_resp)
    payload = {"id": project_id}

    _ = requests.post(f"{HOST}{TODOS}/{todo_id}/tasksof", json=payload, timeout=3)

    r = requests.delete(f"{HOST}{TODOS}/{todo_id}/tasksof/{project_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["projects"] == []


# =====================================
# XML Format Tests
# =====================================

def test_get_todo_categories_xml(todo_server):
    """GET /todos/:id/categories with Accept: application/xml returns XML."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)
    
    new_category_name = generate_title("category")
    create_category_resp = create_category(name=new_category_name)
    category_id = require_created_id(create_category_resp)
    
    payload = {"id": category_id}
    requests.post(f"{HOST}{TODOS}/{todo_id}/categories", json=payload, timeout=3)
    
    r = requests.get(
        f"{HOST}{TODOS}/{todo_id}/categories",
        headers={"Accept": "application/xml"},
        timeout=3
    )
    assert r.status_code == 200
    assert "application/xml" in r.headers.get("Content-Type", "")


def test_post_todo_categories_xml(todo_server):
    """POST /todos/:id/categories with XML creates relationship."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)
    
    new_category_name = generate_title("category")
    create_category_resp = create_category(name=new_category_name)
    category_id = require_created_id(create_category_resp)
    
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<category>
    <id>{category_id}</id>
</category>"""
    
    r = requests.post(
        f"{HOST}{TODOS}/{todo_id}/categories",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3
    )
    assert r.status_code == 201
    
    # Verify relationship
    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}/categories", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert any(c["id"] == category_id for c in body["categories"])


def test_get_todo_tasksof_xml(todo_server):
    """GET /todos/:id/tasksof with Accept: application/xml returns XML."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)
    
    new_project_name = generate_title("project")
    create_project_resp = create_project(name=new_project_name)
    project_id = require_created_id(create_project_resp)
    
    payload = {"id": project_id}
    requests.post(f"{HOST}{TODOS}/{todo_id}/tasksof", json=payload, timeout=3)
    
    r = requests.get(
        f"{HOST}{TODOS}/{todo_id}/tasksof",
        headers={"Accept": "application/xml"},
        timeout=3
    )
    assert r.status_code == 200
    assert "application/xml" in r.headers.get("Content-Type", "")


def test_post_todo_tasksof_xml(todo_server):
    """POST /todos/:id/tasksof with XML creates relationship."""
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)
    
    new_project_name = generate_title("project")
    create_project_resp = create_project(name=new_project_name)
    project_id = require_created_id(create_project_resp)
    
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<project>
    <id>{project_id}</id>
</project>"""
    
    r = requests.post(
        f"{HOST}{TODOS}/{todo_id}/tasksof",
        data=xml_payload,
        headers={"Content-Type": "application/xml"},
        timeout=3
    )
    assert r.status_code == 201
    
    # Verify relationship
    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert any(p["id"] == project_id for p in body["projects"])
