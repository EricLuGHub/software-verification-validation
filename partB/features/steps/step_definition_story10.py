"""

As a user, I want to delete a TODO to clear up future requests.

"""

from behave import given, when, then
from step_utils import (
    extract_collection,
    find_by_title,
    ensure_project_exists,
    ensure_todo_exists,
    ensure_task_relationship,
)


@given('some deletion todo with title {todo_title} exists')
def step_deletion_todo_exists(context, todo_title):
    todo_id = ensure_todo_exists(context, todo_title)
    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[todo_title] = todo_id
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('some deletion project named {project_title} exists')
def step_deletion_project_exists(context, project_title):
    project_id = ensure_project_exists(context, project_title)
    if not hasattr(context, 'project_ids'):
        context.project_ids = {}
    context.project_ids[project_title] = project_id
    context.current_project_title = project_title
    context.current_project_id = project_id


@given('some deletion todo {todo_title} is a task of that project')
def step_deletion_todo_is_task_of_project(context, todo_title):
    project_id = getattr(context, 'current_project_id', None)
    assert project_id is not None, 'Project must be set before creating a relationship'

    todo_id = ensure_todo_exists(context, todo_title)
    ensure_task_relationship(context, project_id, todo_id)

    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[todo_title] = todo_id
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('some deletion todo with title {todo_title} does not exist')
def step_deletion_todo_does_not_exist(context, todo_title):
    r = context.http.get(f"{context.base_url}/todos", params={"title": todo_title}, timeout=5)
    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"

    todos = extract_collection(r.json(), 'todos')
    for todo in todos:
        if isinstance(todo, dict) and todo.get('id'):
            r_delete = context.http.delete(f"{context.base_url}/todos/{todo.get('id')}", timeout=5)
            assert r_delete.status_code in (200, 404), (
                f"Unexpected status deleting todo '{todo_title}' id={todo.get('id')}: "
                f"{r_delete.status_code}, body: {r_delete.text}"
            )

    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[todo_title] = '99999999'
    context.current_todo_title = todo_title
    context.current_todo_id = '99999999'


@when('I delete todo {todo_title}')
def step_delete_todo_by_title(context, todo_title):
    todo_id = None

    todo_id = context.todo_ids.get(todo_title)
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id

    r = context.http.delete(f"{context.base_url}/todos/{todo_id}", timeout=5)
    context.last_response = r


@then('todo with title {todo_title} should not exist')
def step_verify_todo_title_not_exists(context, todo_title):
    r = context.http.get(f"{context.base_url}/todos", params={"title": todo_title}, timeout=5)
    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"

    todos = extract_collection(r.json(), 'todos')
    still_exists = any(
        isinstance(todo, dict) and todo.get('title') == todo_title
        for todo in todos
    )
    assert not still_exists, f"Todo with title '{todo_title}' still exists. Response: {r.json()}"


@then('todo {todo_title} should not be a task of {project_title}')
def step_verify_todo_not_task_of_project(context, todo_title, project_title):
    project_id = None

    if hasattr(context, 'project_ids'):
        project_id = context.project_ids.get(project_title)

    if not project_id:
        r_project = context.http.get(f"{context.base_url}/projects", params={"title": project_title}, timeout=5)
        assert r_project.status_code == 200, (
            f"GET /projects failed: {r_project.status_code}, body: {r_project.text}"
        )
        projects = extract_collection(r_project.json(), 'projects')
        project = find_by_title(projects, project_title)
        assert project is not None, f"Project '{project_title}' not found"
        project_id = project.get('id')

    r_tasks = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    assert r_tasks.status_code == 200, (
        f"GET /projects/{project_id}/tasks failed: {r_tasks.status_code}, body: {r_tasks.text}"
    )

    tasks = extract_collection(r_tasks.json(), 'todos')
    still_related = any(
        isinstance(task, dict) and task.get('title') == todo_title
        for task in tasks
    )
    assert not still_related, (
        f"Todo '{todo_title}' is still a task of project '{project_title}'. Response: {r_tasks.json()}"
    )
