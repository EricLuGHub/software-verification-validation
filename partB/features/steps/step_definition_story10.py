"""

As a user, I want to delete a TODO to clear up future requests.

"""

from behave import given, when, then
from step_utils import (
    extract_collection,
    find_by_title,
    ensure_todo_exists,
    ensure_task_relationship,
)


@when('I delete todo {todo_title}')
def step_delete_todo_by_title(context, todo_title):
    """Delete a todo by title."""
    todo_id = None

    if hasattr(context, 'todo_ids') and context.todo_ids.get(todo_title):
        todo_id = context.todo_ids.get(todo_title)
    
    if not todo_id:
        r_lookup = context.http.get(f"{context.base_url}/todos", params={"title": todo_title}, timeout=5)
        assert r_lookup.status_code == 200, f"GET /todos failed: {r_lookup.status_code}, body: {r_lookup.text}"
        todos = extract_collection(r_lookup.json(), 'todos')
        todo = find_by_title(todos, todo_title)
        todo_id = todo.get('id') if todo else None

    context.current_todo_title = todo_title
    context.current_todo_id = todo_id

    r = context.http.delete(f"{context.base_url}/todos/{todo_id}", timeout=5)
    context.last_response = r


@then('todo with title {todo_title} should not exist')
def step_verify_todo_title_not_exists(context, todo_title):
    """Verify that a todo is not in the system."""
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
    """Verify that a todo is not associated with a project."""
    project_id = None

    if hasattr(context, 'project_ids'):
        project_id = context.project_ids.get(project_title)

    if not project_id:
        r_project = context.http.get(f"{context.base_url}/projects", params={"title": project_title}, timeout=5)
        assert r_project.status_code == 200, (
            f"GET /projects failed: {r_project.status_code}, body: {r_project.text}"
        )
        projects = extract_collection(r_project.json(), "projects")
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

