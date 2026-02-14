import subprocess
import time
import requests
import pytest
import socket
from pathlib import Path
import uuid


HOST = "http://localhost:4567"
PROJECTS = "/projects"
TODOS = "/todos"
CATEGORIES = "/categories"


def is_port_open(host="localhost", port=4567):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def wait_until_ready(timeout_seconds=15):
    deadline = time.time() + timeout_seconds
    url = f"{HOST}{PROJECTS}"

    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=0.5)
            if r.status_code in (200, 404):
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)

    raise RuntimeError("Server did not become ready in time")


def jar_path():
    return Path(__file__).resolve().parents[3] / "runTodoManagerRestAPI-1.5.5.jar"


@pytest.fixture(scope="session")
def todo_server():
    already_running = is_port_open()

    if not already_running:
        p = jar_path()
        proc = subprocess.Popen(
            ["java", "-jar", str(p)],
        )
        wait_until_ready()
    else:
        proc = None

    yield

    if proc is not None:
        proc.terminate()
        proc.wait(timeout=5)


def assert_has_common_headers(response):
    assert "Content-Type" in response.headers
    assert "Date" in response.headers
    assert "Server" in response.headers


def generate_title(prefix="pytest"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def create_project(name=None, description=""):
    if name is None:
        name = generate_title("project")

    payload = {
        "title": name,
        "description": description,
    }

    r = requests.post(f"{HOST}{PROJECTS}", json=payload, timeout=3)
    return r


def create_todo(title=None, doneStatus=False, description="", categories=None, tasksof=None):
    if title is None:
        title = generate_title("todo")

    payload = {
        "title": title,
        "doneStatus": doneStatus,
        "description": description,
    }
    if categories is not None:
        payload["categories"] = categories
    if tasksof is not None:
        payload["tasksof"] = tasksof

    r = requests.post(f"{HOST}{TODOS}", json=payload, timeout=3)
    return r


def create_category(name=None):
    if name is None:
        name = generate_title("category")

    payload = {"title": name}
    r = requests.post(f"{HOST}{CATEGORIES}", json=payload, timeout=3)
    return r


def extract_created_id(resp_json):
    for key in ("id",):
        if key in resp_json:
            return str(resp_json[key])
    return None


def require_created_id(create_resp):
    assert create_resp.status_code == 201
    j = create_resp.json()
    created_id = extract_created_id(j)
    assert created_id is not None
    return created_id


def assert_subset(expected, actual):
    if isinstance(expected, dict):
        assert isinstance(actual, dict)
        for k, v in expected.items():
            assert k in actual
            assert_subset(v, actual[k])
    elif isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(expected) == len(actual)
        for e_item, a_item in zip(expected, actual):
            assert_subset(e_item, a_item)
    else:
        assert expected == actual


def projects_contain_expected(response_json, expected_projects):
    assert "projects" in response_json
    actual_projects = response_json["projects"]

    def matches_subset(expected, actual):
        for k, v in expected.items():
            if isinstance(v, dict):
                if k not in actual or not matches_subset(v, actual[k]):
                    return False
            elif isinstance(v, list):
                if k not in actual:
                    return False
                for expected_item in v:
                    if not any(matches_subset(expected_item, a) for a in actual[k]):
                        return False
            else:
                if actual.get(k) != v:
                    return False
        return True

    for expected in expected_projects:
        assert any(matches_subset(expected, a) for a in actual_projects), \
            f"Expected project not found: {expected}"


##############################
# /projects CRUD
##############################

def test_create_project(todo_server):
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


def test_get_project_by_id_nonexistent(todo_server):
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
    project_id = 0
    r = requests.get(f"{HOST}{PROJECTS}?id={project_id}", timeout=3)
    expected = {"projects": []}
    assert r.status_code == 200
    assert_subset(expected, r.json())


def test_get_project_by_id_filter(todo_server):
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
    r = requests.head(f"{HOST}{PROJECTS}", timeout=3)
    assert r.status_code in (200, 204)
    assert_has_common_headers(r)


def test_get_projects_filter_by_title_query_param(todo_server):
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
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r.status_code == 200
    assert_has_common_headers(r)


def test_post_project_by_id_amends_title(todo_server):
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
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.delete(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{PROJECTS}/{project_id}", timeout=3)
    assert r2.status_code == 404


def test_delete_project_by_id_nonexistent(todo_server):
    r = requests.delete(f"{HOST}{PROJECTS}/0", timeout=3)
    assert r.status_code == 404


##############################
# /projects/:id/tasks
##############################

def test_get_project_tasks_no_link(todo_server):
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
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/tasks", timeout=3)
    assert r.status_code == 200
    if r.status_code == 200:
        assert_has_common_headers(r)


def test_post_project_tasks_creates_relationship(todo_server):
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


##############################
# /projects/:id/categories
##############################

def test_get_project_categories_no_link(todo_server):
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
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/categories", timeout=3)
    assert r.status_code == 200
    if r.status_code == 200:
        assert_has_common_headers(r)


def test_post_project_categories_creates_relationship(todo_server):
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