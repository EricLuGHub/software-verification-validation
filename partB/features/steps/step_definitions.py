import subprocess
import time
import os
import requests
from behave import given, then

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


@given('some project {id} does not exist')
def step_project_does_not_exist(context, id):
    """Verify that a project with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/projects/{id}", timeout=5)
    if r.status_code == 200:
        r_delete = context.http.delete(f"{context.base_url}/projects/{id}", timeout=5)
        assert r_delete.status_code == 200, f"Failed to delete existing project {id}: {r_delete.status_code}, body: {r_delete.text}"


@given('some todo {id} does not exist')
def step_todo_does_not_exist(context, id):
    """Verify that a todo with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/todos/{id}", timeout=5)
    if r.status_code == 200:
        r_delete = context.http.delete(f"{context.base_url}/todos/{id}", timeout=5)
        assert r_delete.status_code == 200, f"Failed to delete existing todo {id}: {r_delete.status_code}, body: {r_delete.text}"


@then('project {id} should not exist')
def step_project_should_not_exist(context, id):
    """Verify that a project with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/projects/{id}", timeout=5)
    assert r.status_code == 404, f"Expected 404 (Not Found), got {r.status_code}, body: {r.text}"


@then('todo {id} should not exist')
def step_todo_should_not_exist(context, id):
    """Verify that a todo with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/todos/{id}", timeout=5)
    assert r.status_code == 404, f"Expected 404 (Not Found), got {r.status_code}, body: {r.text}"

