import subprocess
import time
import requests
import pytest
import socket
from pathlib import Path
import uuid


HOST = "http://localhost:4567"
TODOS = "/todos"
CATEGORIES = "/categories"
PROJECTS = "/projects"


def is_port_open(host="localhost", port=4567):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def wait_until_ready(timeout_seconds=15, endpoint=TODOS):
    deadline = time.time() + timeout_seconds
    url = f"{HOST}{endpoint}"

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
    return Path(__file__).resolve().parents[2] / "runTodoManagerRestAPI-1.5.5.jar"


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
