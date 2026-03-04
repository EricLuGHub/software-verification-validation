"""

As a user, I want to delete a taskof relationship I accidentally created.

"""

import time
from behave import given, when, then


def _extract_items(data, primary_key):
    if isinstance(data, dict):
        items = data.get(primary_key) or data.get(primary_key[:-1]) or data.get("items") or []
        if isinstance(items, dict):
            return [items]
        return items
    if isinstance(data, list):
        return data
    return []


def _find_by_title(items, title):
    for item in items:
        if isinstance(item, dict) and item.get("title") == title:
            return item
    return None


def _ensure_project_exists(context, title):
    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    projects = _extract_items(r.json(), "projects")
    project = _find_by_title(projects, title)
    if project:
        return project.get("id")

    create = context.http.post(f"{context.base_url}/projects", json={"title": title}, timeout=5)
    assert create.status_code == 201, f"Failed to create project '{title}': {create.status_code}, body: {create.text}"
    return create.json().get("id")


def _ensure_todo_exists(context, title):
    r = context.http.get(f"{context.base_url}/todos", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"

    todos = _extract_items(r.json(), "todos")
    todo = _find_by_title(todos, title)
    if todo:
        return todo.get("id")

    create = context.http.post(
        f"{context.base_url}/todos",
        json={"title": title, "doneStatus": False},
        timeout=5,
    )
    assert create.status_code == 201, f"Failed to create todo '{title}': {create.status_code}, body: {create.text}"
    return create.json().get("id")


def _ensure_relationship(context, project_id, todo_id):
    payload = {"id": str(todo_id)}
    r = context.http.post(f"{context.base_url}/projects/{project_id}/tasks", json=payload, timeout=5)
    assert r.status_code in (200, 201), (
        f"Failed to create task relationship project={project_id}, todo={todo_id}: "
        f"{r.status_code}, body: {r.text}"
    )


def _ensure_relationship_absent(context, project_id, todo_id):
    r = context.http.delete(f"{context.base_url}/projects/{project_id}/tasks/{todo_id}", timeout=5)
    assert r.status_code in (200, 404), (
        f"Unexpected status when removing relationship project={project_id}, todo={todo_id}: "
        f"{r.status_code}, body: {r.text}"
    )


@given('some project with title {project_title} exists')
def step_project_exists(context, project_title):
    project_id = _ensure_project_exists(context, project_title)
    context.current_project_title = project_title
    context.current_project_id = project_id


@given('some todo with title {todo_title} exists')
def step_todo_exists(context, todo_title):
    todo_id = _ensure_todo_exists(context, todo_title)
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('todo with title {todo_title} is a task of that project')
def step_todo_is_task_of_project(context, todo_title):
    project_id = getattr(context, "current_project_id", None)
    assert project_id is not None, "Project must be created before creating relationship"

    todo_id = _ensure_todo_exists(context, todo_title)
    _ensure_relationship(context, project_id, todo_id)

    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('some todo is a task of project {project_title}')
def step_some_todo_is_task_of_project(context, project_title):
    project_id = _ensure_project_exists(context, project_title)
    todo_title = f"tmp-task-{int(time.time() * 1000)}"
    todo_id = _ensure_todo_exists(context, todo_title)
    _ensure_relationship(context, project_id, todo_id)

    context.current_project_title = project_title
    context.current_project_id = project_id
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('a taskof relationship between the two does not exist')
def step_no_relationship_between_two(context):
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"
    _ensure_relationship_absent(context, project_id, todo_id)


@when('I delete the relationship between the two from the task\'s side')
def step_delete_relationship_from_task_side(context):
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"

    r = context.http.delete(f"{context.base_url}/todos/{todo_id}/tasksof/{project_id}", timeout=5)
    context.last_response = r


@when('I delete the relationship between the two from the project\'s side')
def step_delete_relationship_from_project_side(context):
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"

    r = context.http.delete(f"{context.base_url}/projects/{project_id}/tasks/{todo_id}", timeout=5)
    context.last_response = r


@then('the request should be accepted')
def step_request_accepted(context):
    r = context.last_response
    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body: {r.text}"


@then('the relationship should no longer exist')
def step_relationship_no_longer_exists(context):
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"

    r = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    assert r.status_code == 200, f"GET /projects/{project_id}/tasks failed: {r.status_code}, body: {r.text}"

    tasks = _extract_items(r.json(), "todos")
    still_related = any(str(item.get("id")) == str(todo_id) for item in tasks if isinstance(item, dict))
    assert not still_related, (
        f"Relationship still exists between project {project_id} and todo {todo_id}. "
        f"Response: {r.json()}"
    )
