"""

As an ECSE 429 student, I want to make a TODO a task of a project
to group the project’s deliverables together.

"""

from behave import when, then
from step_utils import extract_collection, find_by_title


def _resolve_todo_id(context, todo_title):
    """Resolve a todo ID from context by title."""
    if hasattr(context, "todo_ids") and context.todo_ids.get(todo_title):
        return context.todo_ids[todo_title]
    return None


def _resolve_project_id(context, project_ref):
    """Resolve a project ID from context or numeric input."""
    if project_ref.isdigit():
        return project_ref

    if hasattr(context, "project_ids") and context.project_ids.get(project_ref):
        return context.project_ids[project_ref]


@when('I make the todo {todo_title} a task of project {project_ref}')
def step_make_todo_task_of_project(context, todo_title, project_ref):
    """Create a taskof relationship from an existing todo."""
    todo_id = _resolve_todo_id(context, todo_title)
    project_id = _resolve_project_id(context, project_ref)

    payload = {"id": str(project_id)}
    r = context.http.post(f"{context.base_url}/todos/{todo_id}/tasksof", json=payload, timeout=5)
    context.last_response = r

    context.current_todo_title = todo_title
    context.current_todo_id = todo_id
    context.current_project_title = project_ref
    context.current_project_id = project_id


@when('I create some todo {todo_title} as a task of project {project_title}')
def step_create_todo_as_task_of_project(context, todo_title, project_title):
    """Create a todo and link it to a project as taskof."""
    project_id = _resolve_project_id(context, project_title)

    payload = {"title": todo_title, "tasksof": [{"id": str(project_id)}]}
    r = context.http.post(f"{context.base_url}/todos", json=payload, timeout=5)
    context.last_response = r

    if r.status_code in (200, 201):
        todo_id = r.json().get("id")
        if not hasattr(context, "todo_ids"):
            context.todo_ids = {}
        context.todo_ids[todo_title] = todo_id

        context.current_todo_title = todo_title
        context.current_todo_id = todo_id
        context.current_project_title = project_title
        context.current_project_id = project_id


@then('the taskof relationship request should be accepted')
def step_relationship_request_accepted(context):
    """Verify taskof relationship creation is accepted."""
    r = context.last_response
    assert r.status_code in (200, 201), (
        f"Expected 200 or 201 for relationship creation, got {r.status_code}, body: {r.text}"
    )


@then('the todo {todo_title} should be a task of project {project_ref}')
def step_todo_should_be_task_of_project(context, todo_title, project_ref):
    """Verify a specific todo is linked to a specific project."""
    todo_id = _resolve_todo_id(context, todo_title)
    expected_project_id = str(_resolve_project_id(context, project_ref))

    r = context.http.get(f"{context.base_url}/todos/{todo_id}/tasksof", timeout=5)
    assert r.status_code == 200, f"GET /todos/{todo_id}/tasksof failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    found = any(
        isinstance(item, dict) and str(item.get("id")) == expected_project_id
        for item in projects
    )
    assert found, (
        f"Expected project id {expected_project_id} in todo {todo_id} tasksof. "
        f"Response: {r.json()}"
    )


@then('the todo should be a task of that project')
def step_todo_should_be_task_of_current_project(context):
    """Verify current todo is linked to current project."""
    todo_id = getattr(context, "current_todo_id", None)
    project_id = getattr(context, "current_project_id", None)
    assert todo_id is not None and project_id is not None, "Current todo and project must be set"

    r = context.http.get(f"{context.base_url}/todos/{todo_id}/tasksof", timeout=5)
    assert r.status_code == 200, f"GET /todos/{todo_id}/tasksof failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    found = any(
        isinstance(item, dict) and str(item.get("id")) == str(project_id)
        for item in projects
    )
    assert found, (
        f"Expected project id {project_id} in todo {todo_id} tasksof. "
        f"Response: {r.json()}"
    )
