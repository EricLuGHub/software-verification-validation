import subprocess
import time
import requests
import pytest

HOST = "http://localhost:4567"         
TODOS_ENDPOINT = "/todos"               


def wait_until_ready(timeout_seconds=10):
    deadline = time.time() + timeout_seconds
    url = f"{HOST}{TODOS_ENDPOINT}"

    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=0.5)
            if r.status_code in (200, 404):
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)

    raise RuntimeError("Server did not become ready in time")


@pytest.fixture
def todo_server():
    proc = subprocess.Popen(
        ["java", "-jar", "runTodoManagerRestAPI-1.5.5.jar"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    wait_until_ready()

    yield

    try:
        requests.get(f"{HOST}/shutdown", timeout=1)
    except requests.RequestException:
        pass

    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()


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


def test_get_todo_by_id_existing(todo_server):
    todo_id = 1
    r = requests.get(f"{HOST}{TODOS_ENDPOINT}/{todo_id}", timeout=2)

    assert r.status_code == 200
    body = r.json()

    expected = {
        "todos": [
            {
                "id": "1",
                "title": "scan paperwork",
                "doneStatus": "false",
                "description": "",
                "categories": [{"id": "1"}],
                "tasksof": [{"id": "1"}],
            }
        ]
    }

    assert_subset(expected, body)