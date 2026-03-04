"""

As an ECSE 429 student, I want to list all the TODOs related to a project
to know what deliverables are expected.

"""

from behave import given, when, then
from step_utils import (
    extract_collection,
    find_by_title,
    ensure_project_exists,
    ensure_todo_exists,
    ensure_task_relationship,
)


# Generic "some project X exists" step is in step_definitions.py - reused from there
# Generic "some todo X is a task of that project" step is in step_definitions.py - reused from there


@given('some project {project_title} with no tasks exists')
def step_project_exists_no_tasks(context, project_title):
    """Ensure a project exists with no associated tasks."""
    project_id = ensure_project_exists(context, project_title)
    
    # Ensure any existing tasks are removed
    r = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    assert r.status_code == 200, f"GET /projects/{project_id}/tasks failed: {r.status_code}, body: {r.text}"
    
    tasks = extract_collection(r.json(), "todos")
    for task in tasks:
        if isinstance(task, dict) and task.get('id'):
            task_id = task.get('id')
            r_delete = context.http.delete(f"{context.base_url}/projects/{project_id}/tasks/{task_id}", timeout=5)
            assert r_delete.status_code in (200, 404), (
                f"Failed to remove task {task_id} from project {project_id}: "
                f"{r_delete.status_code}, body: {r_delete.text}"
            )
    
    if not hasattr(context, 'project_ids'):
        context.project_ids = {}
    context.project_ids[project_title] = project_id
    context.current_project_title = project_title
    context.current_project_id = project_id


@when('I list tasks of that project')
def step_list_tasks_of_current_project(context):
    """List all tasks of the current project."""
    project_id = getattr(context, 'current_project_id', None)
    assert project_id is not None, 'Project must be set to list tasks'

    r = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    context.last_response = r


@when('I list tasks of project {project_title}')
def step_list_tasks_of_project_by_title(context, project_title):
    """List all tasks of a project by title (lookup if needed)."""
    project_id = None

    # Try to get from stored context first
    if hasattr(context, 'project_ids'):
        project_id = context.project_ids.get(project_title)

    # If not stored, try to lookup by title
    if not project_id:
        r_lookup = context.http.get(f"{context.base_url}/projects", params={"title": project_title}, timeout=5)
        assert r_lookup.status_code == 200, f"GET /projects failed: {r_lookup.status_code}, body: {r_lookup.text}"
        projects = extract_collection(r_lookup.json(), "projects")
        project = find_by_title(projects, project_title)
        project_id = project.get('id') if project else None

    context.current_project_title = project_title
    context.current_project_id = project_id

    r = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    context.last_response = r
