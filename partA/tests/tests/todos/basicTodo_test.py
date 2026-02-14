import subprocess
import time
import requests
import pytest
import socket
from pathlib import Path
import uuid


HOST = "http://localhost:4567"
TODOS = "/todos"


def is_port_open(host="localhost", port=4567):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def wait_until_ready(timeout_seconds=15):
    deadline = time.time() + timeout_seconds
    url = f"{HOST}{TODOS}"

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

# TODO: move to helper function file
def assert_has_common_headers(response):
    assert "Content-Type" in response.headers
    assert "Date" in response.headers
    assert "Server" in response.headers


def generate_title(prefix="pytest"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def create_category(name=None):
    if name is None:
        name = generate_title("category")

    payload = {
        "title": name
    }

    r = requests.post(f"{HOST}/categories", json=payload, timeout=3)
    return r

def create_project(name=None):
    if name is None:
        name = generate_title("project")

    payload = {
        "title": name
    }

    r = requests.post(f"{HOST}/projects", json=payload, timeout=3)
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

def todos_contain_expected(response_json, expected_todos):
    assert "todos" in response_json
    actual_todos = response_json["todos"]

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

    for expected in expected_todos:
        assert any(matches_subset(expected, a) for a in actual_todos), \
            f"Expected todo not found: {expected}"

###################################################

def test_create_todo(todo_server):
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

# TODO: make a post to add then look for it
def test_get_todo_by_id_existing():

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



def test_get_todo_by_id_nonexistent():
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
    todo_id = "abc"
    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=2)
    expected = {
    "errorMessages": [
        "Could not find an instance with todos/abc"
    ]
}
    assert r.status_code == 404
    assert_subset(expected, r.json())

def test_get_todo_by_id_nonexistent_with_id_query():
    todo_id = 0
    r = requests.get(f"{HOST}{TODOS}?id={todo_id}", timeout=2)
    expected = {
    "todos": []
    }

    assert r.status_code == 200
    assert_subset(expected, r.json())

def test_get_todo_by_id_filter():

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

def test_get_todo_filter_by_id_query_nonexistant_param():
    r = requests.get(f"{HOST}{TODOS}?id=0", timeout=3)
    assert r.status_code == 200
    body = r.json()
    expected = {
        "todos": []
    }
    assert_subset(expected, body)


def test_get_todos_returns_all(todo_server):
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


def test_head_todos_returns_headers():
    r = requests.head(f"{HOST}{TODOS}", timeout=3)
    assert r.status_code in (200, 204)
    assert_has_common_headers(r)


def test_get_todos_filter_by_title_query_param():
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

def test_get_todo_by_id_existing():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r.status_code == 200
    _ = r.json()


def test_head_todo_by_id_headers():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r.status_code == 200
    assert_has_common_headers(r)



def test_post_todo_by_id_amends_title():
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

def test_post_todo_by_id_amends_doneStatus():
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

def test_post_todo_by_id_amends_description():
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

def test_post_todo_by_id_amends_multiple_fields():
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

def test_post_todo_not_valid_field():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    payload = {
    "errorMessages": [
        "Could not find field: notvalid"
    ]
}
    r = requests.post(f"{HOST}{TODOS}/{todo_id}", json=payload, timeout=3)
    assert r.status_code == 400


def test_delete_todo_by_id_deletes():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.delete(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r.status_code == 200

    r2 = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=3)
    assert r2.status_code == 404

def test_delete_todo_by_id_nonexistent():
    r = requests.delete(f"{HOST}{TODOS}/0", timeout=3)
    assert r.status_code == 404

def test_get_todo_categories(todo_server):

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


# undocumented
def test_get_todo_categories():
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


def test_head_todo_categories():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{TODOS}/{todo_id}/categories", timeout=3)
    assert r.status_code in (200, 204, 404)
    if r.status_code in (200, 204):
        assert_has_common_headers(r)


def test_post_todo_categories_creates_relationship():
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


def test_delete_todo_category_relationship():
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


def test_get_todo_tasksof_no_link():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r.status_code in (200, 404)
    body = r.json()

    assert r.status_code == 200
    assert "projects" in body
    assert isinstance(body["projects"], list)
    assert body["projects"] == []

def test_get_todo_tasksof():

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


def test_head_todo_tasksof():
    create_resp = create_todo()
    todo_id = require_created_id(create_resp)

    r = requests.head(f"{HOST}{TODOS}/{todo_id}/tasksof", timeout=3)
    assert r.status_code in (200, 204, 404)
    if r.status_code in (200, 204):
        assert_has_common_headers(r)


def test_post_todo_tasksof_creates_relationship():
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


def test_delete_todo_tasksof_relationship():
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