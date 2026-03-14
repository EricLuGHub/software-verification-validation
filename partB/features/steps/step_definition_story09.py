"""

As a user, I want to delete a taskof relationship I accidentally created.

"""

import time
from behave import given, when, then
from step_utils import (
    extract_collection,
    ensure_project_exists,
    ensure_todo_exists,
    ensure_task_relationship,
    ensure_task_relationship_absent,
)


@given('todo with title {todo_title} is a task of that project')
def step_todo_is_task_of_project(context, todo_title):
    """Ensure a todo is linked as a task of current project."""
    project_id = getattr(context, "current_project_id", None)
    assert project_id is not None, "Project must be created before creating relationship"

    todo_id = ensure_todo_exists(context, todo_title)
    ensure_task_relationship(context, project_id, todo_id)

    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('some todo is a task of project {project_title}')
def step_some_todo_is_task_of_project(context, project_title):
    """Create and link a temporary todo to a project."""
    project_id = ensure_project_exists(context, project_title)
    todo_title = f"tmp-task-{int(time.time() * 1000)}"
    todo_id = ensure_todo_exists(context, todo_title)
    ensure_task_relationship(context, project_id, todo_id)

    context.current_project_title = project_title
    context.current_project_id = project_id
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id


@given('a taskof relationship between the two does not exist')
def step_no_relationship_between_two(context):
    """Ensure no task relationship exists for current pair."""
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"
    ensure_task_relationship_absent(context, project_id, todo_id)


@when('I delete the relationship between the two from the task\'s side')
def step_delete_relationship_from_task_side(context):
    """Delete task relationship via the todo endpoint."""
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"

    r = context.http.delete(f"{context.base_url}/todos/{todo_id}/tasksof/{project_id}", timeout=5)
    context.last_response = r


@when('I delete the relationship between the two from the project\'s side')
def step_delete_relationship_from_project_side(context):
    """Delete task relationship via the project endpoint."""
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"

    r = context.http.delete(f"{context.base_url}/projects/{project_id}/tasks/{todo_id}", timeout=5)
    context.last_response = r


@then('the relationship should no longer exist')
def step_relationship_no_longer_exists(context):
    """Verify the project-todo relationship was removed."""
    project_id = getattr(context, "current_project_id", None)
    todo_id = getattr(context, "current_todo_id", None)
    assert project_id is not None and todo_id is not None, "Project and todo must exist first"

    r = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    assert r.status_code == 200, f"GET /projects/{project_id}/tasks failed: {r.status_code}, body: {r.text}"

    tasks = extract_collection(r.json(), "todos")
    still_related = any(str(item.get("id")) == str(todo_id) for item in tasks if isinstance(item, dict))
    assert not still_related, (
        f"Relationship still exists between project {project_id} and todo {todo_id}. "
        f"Response: {r.json()}"
    )
