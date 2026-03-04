"""

As an ECSE 429 student, I want to be able to mark a TODO as complete
to keep track of what's already been done.

"""

from behave import when, then, given

@given('a todo with title {title} exists')
def step_todo_with_title_exists(context, title):
    """Ensure a todo with the given title exists."""
    r = context.http.get(f"{context.base_url}/todos", params={"title": title}, timeout=5)
    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"

    data = r.json()

    for item in data.get("todos", []):
        if item.get("title") == title:
            if not hasattr(context, 'todo_ids'):
                context.todo_ids = {}
            context.todo_ids[title] = item.get("id")
            return

    payload = {"title": title, "doneStatus": False}
    r = context.http.post(f"{context.base_url}/todos", json=payload, timeout=5)
    assert r.status_code == 201, f"Failed to create todo '{title}': {r.status_code}, body: {r.text}"
    
    response_data = r.json()
    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[title] = response_data.get("id")


@when('I mark todo {title} as complete')
def step_mark_todo_complete(context, title):
    """Mark a todo as complete by title."""
    todo_id = context.todo_ids.get(title)
    
    payload = {"doneStatus": True}
    r = context.http.post(f"{context.base_url}/todos/{todo_id}", json=payload, timeout=5)
    context.last_response = r


@then('todo {title} should be marked as complete')
def step_verify_todo_complete(context, title):
    """Verify that a todo is marked as complete."""
  
    todo_id = context.todo_ids.get(title)
    
    r = context.http.get(f"{context.base_url}/todos/{todo_id}", timeout=5)

    assert r.status_code == 200, f"GET /todos failed: {r.status_code}, body: {r.text}"
    
    data = r.json()
    todos = data.get("todos", [])
    if todos and len(todos) > 0:
        todo = todos[0]
    
    done_status = todo.get("doneStatus")
    is_complete = done_status == "true"
    assert is_complete, f"Todo '{title}' is not marked as complete. doneStatus: {done_status}"


@when('I create a todo with title {title} and mark as complete')
def step_create_todo_marked_complete(context, title):
    """Create a new todo that is already marked as complete."""
    payload = {"title": title, "doneStatus": True}
    r = context.http.post(f"{context.base_url}/todos", json=payload, timeout=5)
    context.last_response = r
    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"
    
    response_data = r.json()
    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[title] = response_data.get("id")


@then('the todo {title} should be returned')
def step_verify_todo_returned(context, title):
    """Verify that the last response contains the todo."""
    r = context.last_response
    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"
    
    data = r.json()
    assert data.get("title") == title, f"Expected title '{title}', got '{data.get('title')}'"


@then('todo {title} should exist with the correct id')
def step_verify_todo_exists_with_id(context, title):
    """Verify that the todo exists and has an ID."""
    todo_id = context.todo_ids.get(title)
    assert todo_id, f"No ID stored for todo '{title}'"
    
    r = context.http.get(f"{context.base_url}/todos/{todo_id}", timeout=5)
    assert r.status_code == 200, f"GET /todos/{todo_id} failed: {r.status_code}, body: {r.text}"
    
    data = r.json()
    todos = data.get("todos", [])
    if todos and len(todos) > 0:
        todo = todos[0]

    
    assert todo.get("id") == todo_id, f"Expected ID '{todo_id}', got '{todo.get('id')}'"
    assert todo.get("title") == title, f"Expected title '{title}', got '{todo.get('title')}'"


@given('some todo {id} does not exist')
def step_todo_does_not_exist(context, id):
    """Verify that a todo with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/todos/{id}", timeout=5)
    if r.status_code == 200:
        r_delete = context.http.delete(f"{context.base_url}/todos/{id}", timeout=5)
        assert r_delete.status_code == 200, f"Failed to delete existing todo {id}: {r_delete.status_code}, body: {r_delete.text}"


@when('I make todo with id {id} marked as complete')
def step_mark_nonexistent_todo_complete(context, id):
    """Attempt to mark a nonexistent todo as complete."""
    payload = {"doneStatus": True}
    r = context.http.post(f"{context.base_url}/todos/{id}", json=payload, timeout=5)
    context.last_response = r


@then('todo {id} should not exist')
def step_todo_should_not_exist(context, id):
    """Verify that a todo with the given ID does not exist."""
    r = context.http.get(f"{context.base_url}/todos/{id}", timeout=5)
    assert r.status_code == 404, f"Expected 404 (Not Found), got {r.status_code}, body: {r.text}"

