"""

As an ECSE 429 student, I want to create a project
to keep track of the deliverables for one part of the term project.

"""

from behave import when, then, given


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

    items = []
    if isinstance(data, dict):
        items = data.get("projects") or data.get("project") or data.get("items") or []
        if isinstance(items, dict):
            items = [items]
    elif isinstance(data, list):
        items = data

    found = any((isinstance(x, dict) and x.get("title") == title and x.get("id") == context.last_response.json().get("id")) for x in items)
    assert found, f'Project "{title}" not found in response: {data}'


@given('some project {title} exists')
def step_project_exists(context, title):
    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    data = r.json()

    for item in data.get("projects", []):
        if item.get("title") == title:
            return

    payload = {"title": title}
    r = context.http.post(f"{context.base_url}/projects", json=payload, timeout=5)
    assert r.status_code == 201, f"Failed to create project '{title}': {r.status_code}, body: {r.text}"


@when('I rename project {old_title} to {new_title}')
def step_rename_project(context, old_title, new_title):
    r = context.http.get(f"{context.base_url}/projects", params={"title": old_title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    data = r.json()

    project_id = None
    for item in data.get("projects", []):
        if isinstance(item, dict) and item.get("title") == old_title:
            project_id = item.get("id")
            break

    if not project_id:
        raise AssertionError(f"Project '{old_title}' not found")
    
    payload = {"title": new_title}
    r = context.http.put(f"{context.base_url}/projects/{project_id}", json=payload, timeout=5)
    context.last_response = r
    assert r.status_code == 200, f"Failed to rename project '{old_title}' to '{new_title}': {r.status_code}, body: {r.text}"


@given('some project {id} does not exist')
def step_project_does_not_exist(context, id):
    """Verify that a project with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/projects/{id}", timeout=5)

    if r.status_code == 200:
        r_delete = context.http.delete(f"{context.base_url}/projects/{id}", timeout=5)
        assert r_delete.status_code == 200, f"Failed to delete existing project {id}: {r_delete.status_code}, body: {r_delete.text}"


@when('I create some project with id {id}')
def step_create_project_with_id(context, id):
    """Attempt to create a project with a specific ID."""
    payload = {"id": id, "title": "Test Project"}
    r = context.http.post(f"{context.base_url}/projects", json=payload, timeout=5)
    context.last_response = r


@then('the request should be refused')
def step_request_refused(context):
    """Verify that the last request was refused (400 error)."""
    r = context.last_response
    assert r.status_code == 400, f"Expected 400 (Bad Request), got {r.status_code}, body: {r.text}"


@then('project {id} should not exist')
def step_project_should_not_exist(context, id):
    """Verify that a project with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/projects/{id}", timeout=5)
    assert r.status_code == 404, f"Expected 404 (Not Found), got {r.status_code}, body: {r.text}"
