"""

As a user, I want to change the title of a project
to make it consistent with the other projects.

"""

from behave import when, then, given
from step_utils import extract_collection, find_by_title


def _lookup_project_by_title(context, title):
    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    project = find_by_title(projects, title)
    return project


@given('some project {title} exists with description {description}')
def step_project_exists_with_description(context, title, description):
    """Ensure a project with the given title and description exists."""
    payload = {"title": title}
    if description:
        payload["description"] = description

    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    existing = None
    for item in projects:
        if isinstance(item, dict) and item.get("title") == title:
            existing = item
            break

    if existing:
        project_id = existing.get("id")
    else:
        create = context.http.post(f"{context.base_url}/projects", json=payload, timeout=5)
        assert create.status_code == 201, f"Failed to create project '{title}': {create.status_code}, body: {create.text}"
        project_id = create.json().get("id")

    if not hasattr(context, 'project_ids'):
        context.project_ids = {}
    context.project_ids[title] = project_id
    context.current_project_title = title
    context.current_project_id = project_id


@when('I change project {title} title to {title_b} through a POST request')
def step_change_project_title_post(context, title, title_b):
    project = _lookup_project_by_title(context, title)
    if project is not None:
        project_id = project.get("id")
        assert project_id is not None, f"Project '{title}' has no id"

        context.story04_target_project_id = str(project_id)
        context.story04_before_project = dict(project)
    else:
        project_id = "999999"
        context.story04_target_project_id = None
        context.story04_before_project = None
        context.story04_before_all_projects = None

    payload = {"title": title_b}
    r = context.http.post(f"{context.base_url}/projects/{project_id}", json=payload, timeout=5)
    context.last_response = r


@when('I change project {title} title to {title_b} through a PUT request')
def step_change_project_title_put(context, title, title_b):
    project = _lookup_project_by_title(context, title)
    if project is not None:
        project_id = project.get("id")
        assert project_id is not None, f"Project '{title}' has no id"

        context.story04_target_project_id = str(project_id)
        context.story04_before_project = dict(project)
    else:
        project_id = "999999"
        context.story04_target_project_id = None
        context.story04_before_project = None
        context.story04_before_all_projects = None

    payload = {"title": title_b}
    
    r = context.http.put(f"{context.base_url}/projects/{project_id}", json=payload, timeout=5)
    context.last_response = r


@then('its title should be {title_b}')
def step_verify_project_title_changed(context, title_b):
    project_id = getattr(context, "story04_target_project_id", None)
    assert project_id is not None, "No target project id stored for title verification"

    r = context.http.get(f"{context.base_url}/projects/{project_id}", timeout=5)
    assert r.status_code == 200, f"GET /projects/{project_id} failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    assert projects, f"No project returned for id={project_id}: {r.json()}"

    updated = projects[0]
    assert updated.get("title") == title_b, (
        f"Expected title '{title_b}', got '{updated.get('title')}'"
    )


@then('nothing else should change for project {title}')
def step_verify_nothing_else_changed(context, title):
    project_id = getattr(context, "story04_target_project_id", None)
    before_project = getattr(context, "story04_before_project", None)

    r = context.http.get(f"{context.base_url}/projects/{project_id}", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects/{project_id} failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    assert projects, f"No project returned for id={project_id}: {r.json()}"

    after_project = projects[0]

    before_copy = dict(before_project)
    after_copy = dict(after_project)
    before_copy.pop("title", None)
    after_copy.pop("title", None)

    assert before_copy == after_copy, (
        f"Fields other than title changed. Before={before_copy}, After={after_copy}"
    )
    

@then('project titled {project} should not exist')
def step_verify_project_title_not_exists(context, project):
    r = context.http.get(f"{context.base_url}/projects", params={"title": project}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    still_exists = any(
        isinstance(item, dict) and item.get("title") == project
        for item in projects
    )
    assert not still_exists, f"Project '{project}' still exists. Response: {r.json()}"
