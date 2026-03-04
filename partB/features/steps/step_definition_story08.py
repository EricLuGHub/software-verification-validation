"""

As an ECSE 429 student, I want to be able to list out all incomplete TODOs
to keep track of what still needs to be done.

"""

from behave import given, when, then
from step_utils import extract_collection


def _is_incomplete(todo):
    return todo.get("doneStatus") == "false"


@given('some todo with title {title} exists marked as complete')
def step_todo_exists_complete(context, title):
    payload = {"title": title, "doneStatus": True}
    r = context.http.post(f"{context.base_url}/todos", json=payload, timeout=5)
    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"


@given('some todo with title {title} exists marked as incomplete')
def step_todo_exists_incomplete(context, title):
    payload = {"title": title, "doneStatus": False}
    r = context.http.post(f"{context.base_url}/todos", json=payload, timeout=5)
    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"


@when('I list every todo marked as incomplete')
def step_list_incomplete_todos(context):
    r = context.http.get(f"{context.base_url}/todos", params={"doneStatus": "false"}, timeout=5)
    context.last_response = r


@then('todo {title} should not be returned')
def step_todo_should_not_be_returned(context, title):
    r = context.last_response
    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body: {r.text}"

    data = r.json()
    todos = extract_collection(data, "todos")

    found = any(isinstance(item, dict) and item.get("title") == title for item in todos)
    assert not found, f"Did not expect todo '{title}' in response, got: {data}"


@when('I list every todo marked as {invalid_status}')
def step_list_invalid_status(context, invalid_status):
    r = context.http.get(f"{context.base_url}/todos", params={"doneStatus": invalid_status}, timeout=5)
    context.last_response = r
