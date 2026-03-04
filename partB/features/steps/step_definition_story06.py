"""

As an ECSE 429 student, I want to create a project
to keep track of the deliverables for one part of the term project.

"""

from behave import when, then, given
from step_utils import extract_collection, find_by_title


@when('I create some project with title {title}')
def step_create_project(context, title):
    payload = {"title": title}
    r = context.http.post(f"{context.base_url}/projects", json=payload, timeout=5)
    context.last_response = r

    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"


@then('the project {title} should be created successfully')
def step_verify_project(context, title):
    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    data = r.json()
    items = extract_collection(data, "projects")

    found = any((isinstance(x, dict) and x.get("title") == title and x.get("id") == context.last_response.json().get("id")) for x in items)
    assert found, f'Project "{title}" not found in response: {data}'


@when('I rename project {old_title} to {new_title}')
def step_rename_project(context, old_title, new_title):
    r = context.http.get(f"{context.base_url}/projects", params={"title": old_title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    data = r.json()
    projects = extract_collection(data, "projects")
    project = find_by_title(projects, old_title)
    project_id = project.get("id") if project else None

    if not project_id:
        raise AssertionError(f"Project '{old_title}' not found")
    
    payload = {"title": new_title}
    r = context.http.put(f"{context.base_url}/projects/{project_id}", json=payload, timeout=5)
    context.last_response = r
    assert r.status_code == 200, f"Failed to rename project '{old_title}' to '{new_title}': {r.status_code}, body: {r.text}"


@when('I create some project with id {id}')
def step_create_project_with_id(context, id):
    """Attempt to create a project with a specific ID."""
    payload = {"id": id, "title": "Test Project"}
    r = context.http.post(f"{context.base_url}/projects", json=payload, timeout=5)
    context.last_response = r
