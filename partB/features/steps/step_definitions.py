import subprocess
import time
import os
import requests
from behave import given, then
from step_utils import ensure_project_exists, ensure_todo_exists, extract_collection, ensure_task_relationship

# TODO: add guardrail for if service is already running on 4567
@given('the API service is running')
def step_api_service_running(context):
    """Start the Todo Manager REST API service."""
    time.sleep(0.5)
    
    if not hasattr(context, 'api_process') or context.api_process is None:
        partb_dir = os.path.join(os.path.dirname(__file__), '..')
        jar_path = os.path.join(partb_dir, 'runTodoManagerRestAPI-1.5.5.jar')
        
        context.api_process = subprocess.Popen(
            ['java', '-jar', jar_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        max_retries = 10
        for attempt in range(max_retries):
            time.sleep(1)
            
            if context.api_process.poll() is not None:
                _, stderr = context.api_process.communicate()
                raise RuntimeError(f"API service crashed. Error: {stderr}")
            
            try:
                response = requests.get('http://localhost:4567/todos', timeout=1)
                if response.status_code == 200:
                    return
            except Exception:
                pass
        
        raise RuntimeError("API service failed to start after waiting 10 seconds")
    
@then('the request should be refused')
def step_request_refused(context):
    """Verify that the last request was refused (400 error)."""
    r = context.last_response
    assert r.status_code in (400, 404), f"Expected 400 or 404 (Bad Request or Not Found), got {r.status_code}, body: {r.text}"


@given('the default objects have been removed')
def step_default_objects_removed(context):
    """Remove default todos created by the API (IDs 1 and 2)."""
    for todo_id in ("1", "2"):
        r = context.http.get(f"{context.base_url}/todos/{todo_id}", timeout=5)
        assert r.status_code in (200, 404), (
            f"Unexpected status while checking default todo {todo_id}: "
            f"{r.status_code}, body: {r.text}"
        )

        if r.status_code == 200:
            r_delete = context.http.delete(f"{context.base_url}/todos/{todo_id}", timeout=5)
            assert r_delete.status_code == 200, (
                f"Failed to delete default todo {todo_id}: "
                f"{r_delete.status_code}, body: {r_delete.text}"
            )


@then('the request should be accepted')
def step_request_accepted(context):
    """Verify that the last request was accepted (200 OK)."""
    r = context.last_response
    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body: {r.text}"


@given('some project with id {id} does not exist')
def step_project_id_does_not_exist(context, id):
    """Verify that a project with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/projects/{id}", timeout=5)
    if r.status_code == 200:
        r_delete = context.http.delete(f"{context.base_url}/projects/{id}", timeout=5)
        assert r_delete.status_code == 200, f"Failed to delete existing project {id}: {r_delete.status_code}, body: {r_delete.text}"


@given('some todo with id {id} does not exist')
def step_todo_id_does_not_exist(context, id):
    """Verify that a todo with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/todos/{id}", timeout=5)
    if r.status_code == 200:
        r_delete = context.http.delete(f"{context.base_url}/todos/{id}", timeout=5)
        assert r_delete.status_code == 200, f"Failed to delete existing todo {id}: {r_delete.status_code}, body: {r_delete.text}"


@then('project with id {id} should not exist')
def step_project_id_should_not_exist(context, id):
    """Verify that a project with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/projects/{id}", timeout=5)
    assert r.status_code == 404, f"Expected 404 (Not Found), got {r.status_code}, body: {r.text}"


@then('todo with id {id} should not exist')
def step_todo_id_should_not_exist(context, id):
    """Verify that a todo with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/todos/{id}", timeout=5)
    assert r.status_code == 404, f"Expected 404 (Not Found), got {r.status_code}, body: {r.text}"


@given('some project {title} exists')
def step_generic_project_exists(context, title):
    """Ensure a project with the given title exists (reusable across all stories)."""
    project_id = ensure_project_exists(context, title)
    if not hasattr(context, 'project_ids'):
        context.project_ids = {}
    context.project_ids[title] = project_id
    context.current_project_title = title
    context.current_project_id = project_id


@given('some project {title} does not exist')
def step_generic_project_does_not_exist(context, title):
    """Ensure a project with the given title does not exist (reusable across all stories)."""
    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    for project in projects:
        if isinstance(project, dict) and project.get('title') == title:
            project_id = project.get('id')
            r_delete = context.http.delete(f"{context.base_url}/projects/{project_id}", timeout=5)
            assert r_delete.status_code == 200, (
                f"Failed to delete project '{title}' id={project_id}: "
                f"{r_delete.status_code}, body: {r_delete.text}"
            )

    if not hasattr(context, 'project_ids'):
        context.project_ids = {}
    context.project_ids[title] = None



@given('some todo {title} exists')
def step_generic_todo_exists(context, title):
    """Ensure a todo with the given title exists (reusable across all stories)."""
    todo_id = ensure_todo_exists(context, title, done_status=False)
    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[title] = todo_id
    context.current_todo_title = title
    context.current_todo_id = todo_id


@given('some todo {title} does not exist')
def step_generic_todo_does_not_exist(context, title):
    """Ensure a todo with the given title does not exist (reusable across all stories)."""
    r = context.http.get(f"{context.base_url}/todos", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"

    todos = extract_collection(r.json(), "todos")
    for todo in todos:
        if isinstance(todo, dict) and todo.get('title') == title:
            todo_id = todo.get('id')
            r_delete = context.http.delete(f"{context.base_url}/todos/{todo_id}", timeout=5)
            assert r_delete.status_code in (200, 404), (
                f"Failed to delete todo '{title}' id={todo_id}: "
                f"{r_delete.status_code}, body: {r_delete.text}"
            )

    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[title] = None


@then('todo {title} should be returned')
def step_generic_todo_should_be_returned(context, title):
    """Verify that a todo is in the returned list (reusable across all stories)."""
    r = context.last_response
    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body: {r.text}"

    data = r.json()
    todos = extract_collection(data, "todos")

    found = any(isinstance(item, dict) and item.get("title") == title for item in todos)
    assert found, f"Expected todo '{title}' in response, got: {data}"


@then('nothing should be returned')
def step_generic_nothing_should_be_returned(context):
    """Verify that the todo/task list is empty (reusable across all stories)."""
    r = context.last_response
    assert r.status_code == 200, f"Expected 200, got {r.status_code}, body: {r.text}"

    data = r.json()
    todos = extract_collection(data, "todos")

    assert len(todos) == 0, f"Expected empty list, got: {data}"


@given('some todo {title} is a task of that project')
def step_generic_todo_is_task_of_project(context, title):
    """Ensure a todo exists and is a task of the current project (reusable across all stories)."""
    project_id = getattr(context, 'current_project_id', None)
    assert project_id is not None, 'Project must be set before creating a relationship'

    todo_id = ensure_todo_exists(context, title)
    ensure_task_relationship(context, project_id, todo_id)

    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[title] = todo_id
    context.current_todo_title = title
    context.current_todo_id = todo_id
