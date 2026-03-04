"""

As an ECSE 429 student, I want to list all the TODOs related to a project
to know what deliverables are expected.

"""

from behave import given, when, then
from step_utils import ensure_project_exists


@given('some project {project_title} with no tasks exists')
def step_project_exists_no_tasks(context, project_title):
    """Ensure a project exists with no associated tasks."""
    project_id = ensure_project_exists(context, project_title)
    
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

    if hasattr(context, 'project_ids'):
        project_id = context.project_ids.get(project_title)

    context.current_project_title = project_title
    context.current_project_id = project_id

    r = context.http.get(f"{context.base_url}/projects/{project_id}/tasks", timeout=5)
    context.last_response = r
