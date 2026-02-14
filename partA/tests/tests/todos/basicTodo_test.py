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

def assert_has_common_headers(response):
    assert "Content-Type" in response.headers
    assert "Date" in response.headers
    assert "Server" in response.headers


def generate_title(prefix="pytest"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def create_todo(title=None, doneStatus=False, description=""):
    if title is None:
        title = generate_title("todo")

    payload = {
        "title": title,
        "doneStatus": doneStatus,
        "description": description,
    }

    r = requests.post(f"{HOST}{TODOS}", json=payload, timeout=3)
    return r


def extract_created_id(resp_json):
    for key in ("id",):
        if key in resp_json:
            return str(resp_json[key])
    return None


def require_created_id(create_resp):
    assert create_resp.status_code in (200, 201)
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


def test_create_todo(todo_server):
    title = generate_title("create")
    r = create_todo(title=title)
    assert r.status_code in (200, 201)
    body = r.json()
    expected = {
        "id": str(int(body.get("id", "0"))),  
        "title": title,
        "doneStatus": "false",
        "description": ""
    }
    assert_subset(expected, body)

# TODO: make a post to add then look for it
def test_get_todo_by_id_existing(todo_server):

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



def test_get_todo_by_id_nonexistent(todo_server):
    todo_id = 9999
    r = requests.get(f"{HOST}{TODOS}/{todo_id}", timeout=2)
    expected = {
    "errorMessages": [
        "Could not find an instance with todos/9999"
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

def test_get_todos_returns_all(todo_server):
    r = requests.get(f"{HOST}{TODOS}", timeout=3)
    assert r.status_code == 200
    _ = r.json()


def test_head_todos_returns_headers(todo_server):
    r = requests.head(f"{HOST}{TODOS}", timeout=3)
    assert r.status_code in (200, 204)
    assert_has_common_headers(r)


def test_get_todos_filter_by_title_query_param(todo_server):
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
    


