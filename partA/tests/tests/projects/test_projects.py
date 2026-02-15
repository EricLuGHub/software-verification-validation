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
    require_created_id,
    assert_subset,
    projects_contain_expected,
)


def test_create_project(todo_server):
    """POST /projects creates a new project with title."""
    title = generate_title("create-project")
    r = create_project(name=title)
    assert r.status_code == 201
    body = r.json()
    expected = {
        "id": str(int(body.get("id", "0"))),
        "title": title,
        "description": ""
    }
    assert_subset(expected, body)


def test_get_project_by_id_existing(todo_server):
    """GET /projects/:id returns the specific project."""
    title = generate_title("get-project-by-id")
    create_resp = create_project(name=title)
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected = {
        "projects": [
            {
                "id": str(int(project_id)),
                "title": title,
                "description": ""
            }
        ]
    }
    assert_subset(expected, body)


def test_get_project_by_id_filter(todo_server):
    """GET /projects/:id?id=X filters by query parameter."""
    title = generate_title("get-project-by-id-filter")
    create_resp = create_project(name=title)
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}/{project_id}?id={project_id}", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected = {
        "projects": [
            {
                "title": title,
                "description": ""
            }
        ]
    }
    assert_subset(expected, body)


def test_get_projects_returns_all(todo_server):
    """GET /projects returns all created projects."""
    p1_title = generate_title("get-all-project-1")
    p2_title = generate_title("get-all-project-2")

    create_resp1 = create_project(name=p1_title)
    create_resp2 = create_project(name=p2_title)
    p1_id = require_created_id(create_resp1)
    p2_id = require_created_id(create_resp2)

    r = requests.get(f"{HOST}{PROJECTS}", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected_p1 = {
        "id": str(int(p1_id)),
        "title": p1_title,
        "description": ""
    }
    expected_p2 = {
        "id": str(int(p2_id)),
        "title": p2_title,
        "description": ""
    }

    projects_contain_expected(body, [expected_p1, expected_p2])


def test_head_projects_returns_headers(todo_server):
    """HEAD /projects returns headers only."""
    r = requests.head(f"{HOST}{PROJECTS}", timeout=3)
    assert r.status_code in (200, 204)
    assert_has_common_headers(r)


def test_get_projects_filter_by_title_query_param(todo_server):
    """GET /projects?title=X filters by title query parameter."""
    title = generate_title("project-query-param")
    create_resp = create_project(name=title)
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}?title={requests.utils.quote(title)}", timeout=3)
    assert r.status_code == 200
    body = r.json()

    expected = {
        "projects": [
            {
                "id": str(int(project_id)),
                "title": title,
                "description": ""
            }
        ]
    }
    assert_subset(expected, body)


def test_head_project_by_id_headers(todo_server):
    """HEAD /projects/:id returns headers only."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r.status_code == 200
    assert_has_common_headers(r)


def test_post_project_by_id_amends_title(todo_server):
    """POST /projects/:id updates project title."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-project-title"),
    }
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["projects"][0]["title"] == payload["title"]


def test_post_project_by_id_amends_description(todo_server):
    """POST /projects/:id updates project description."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "description": generate_title("amend-project-desc"),
    }
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["projects"][0]["description"] == payload["description"]


def test_post_project_by_id_amends_multiple_fields(todo_server):
    """POST /projects/:id updates multiple project fields."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-project-multi"),
        "description": generate_title("amend-project-multi-desc")
    }
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["projects"][0]["title"] == payload["title"]
    assert body["projects"][0]["description"] == payload["description"]


def test_put_project_by_id_amends_fields(todo_server):
    """PUT /projects/:id updates project fields."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-project-put"),
        "description": generate_title("amend-project-put-desc"),
    }
    r = requests.put(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r2.status_code == 200
    body = r2.json()
    assert body["projects"][0]["title"] == payload["title"]
    assert body["projects"][0]["description"] == payload["description"]


def test_delete_project_by_id_deletes(todo_server):
    """DELETE /projects/:id removes the project."""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.delete(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r2.status_code == 404
