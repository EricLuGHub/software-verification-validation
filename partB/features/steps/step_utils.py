def extract_collection(data, primary_key):
    """Return a normalized list from API response data."""
    if isinstance(data, dict):
        singular_key = primary_key[:-1] if primary_key.endswith("s") else primary_key
        items = data.get(primary_key) or data.get(singular_key) or data.get("items") or []
        if isinstance(items, dict):
            return [items]
        return items
    if isinstance(data, list):
        return data
    return []


def find_by_title(items, title):
    """Return the first item whose title matches."""
    for item in items:
        if isinstance(item, dict) and item.get("title") == title:
            return item
    return None


def ensure_project_exists(context, title):
    """Get or create a project by title and return its ID."""
    r = context.http.get(f"{context.base_url}/projects", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /projects failed: {r.status_code}, body: {r.text}"

    projects = extract_collection(r.json(), "projects")
    existing = find_by_title(projects, title)
    if existing:
        return existing.get("id")

    create = context.http.post(f"{context.base_url}/projects", json={"title": title}, timeout=5)
    assert create.status_code == 201, f"Failed to create project '{title}': {create.status_code}, body: {create.text}"
    return create.json().get("id")


def ensure_todo_exists(context, title, done_status=False):
    """Get or create a todo by title and return its ID."""
    r = context.http.get(f"{context.base_url}/todos", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"

    todos = extract_collection(r.json(), "todos")
    existing = find_by_title(todos, title)
    if existing:
        return existing.get("id")

    create = context.http.post(
        f"{context.base_url}/todos",
        json={"title": title, "doneStatus": done_status},
        timeout=5,
    )
    assert create.status_code == 201, f"Failed to create todo '{title}': {create.status_code}, body: {create.text}"
    return create.json().get("id")


def ensure_task_relationship(context, project_id, todo_id):
    """Ensure a todo is linked as a task of a project."""
    payload = {"id": str(todo_id)}
    r = context.http.post(f"{context.base_url}/projects/{project_id}/tasks", json=payload, timeout=5)
    assert r.status_code in (200, 201), (
        f"Failed to create task relationship project={project_id}, todo={todo_id}: "
        f"{r.status_code}, body: {r.text}"
    )


def ensure_task_relationship_absent(context, project_id, todo_id):
    """Ensure a task relationship between project and todo is absent."""
    r = context.http.delete(f"{context.base_url}/projects/{project_id}/tasks/{todo_id}", timeout=5)
    assert r.status_code in (200, 404), (
        f"Unexpected status when removing relationship project={project_id}, todo={todo_id}: "
        f"{r.status_code}, body: {r.text}"
    )
