"""

As a McGill student, I want to change the due date in the description of a TODO
since I was allowed an extension.

"""

from behave import given, when, then
from step_utils import extract_collection, ensure_todo_exists


@given('some todo {todo_title} exists with description {description}')
def step_todo_exists_with_description(context, todo_title, description):
    """Ensure a todo with the given title and description exists."""
    
    payload = {"title": todo_title}
    if description:  
        payload["description"] = description
    
    create = context.http.post(f"{context.base_url}/todos", json=payload, timeout=5)
    assert create.status_code == 201, f"Failed to create todo '{todo_title}': {create.status_code}, body: {create.text}"
    todo_id = create.json().get("id")

    if not hasattr(context, 'todo_ids'):
        context.todo_ids = {}
    context.todo_ids[todo_title] = todo_id
    context.current_todo_title = todo_title
    context.current_todo_id = todo_id

@given('some todo {todo_title} exists with no description')
def step_todo_exists_with_no_description(context, todo_title):
    """Ensure a todo with the given title exists and has no description."""
    step_todo_exists_with_description(context, todo_title, description=None)



@when('I change todo {todo_title} description to {new_description}')
def step_change_todo_description(context, todo_title, new_description):
    """Change the description of a todo by title."""
    todo_id = context.todo_ids.get(todo_title)
    assert todo_id is not None, f"Todo '{todo_title}' must exist before changing description"
    
    payload = {"description": new_description}
    r = context.http.post(f"{context.base_url}/todos/{todo_id}", json=payload, timeout=5)
    context.last_response = r


@when('I change its description to {new_description}')
def step_change_current_todo_description(context, new_description):
    """Change the description of the current todo (from context)."""
    todo_id = getattr(context, 'current_todo_id', None)
    assert todo_id is not None, "A todo must be set in context before changing its description"
    
    payload = {"description": new_description}
    r = context.http.post(f"{context.base_url}/todos/{todo_id}", json=payload, timeout=5)
    context.last_response = r


@then('it should have description {expected_description}')
def step_verify_todo_description(context, expected_description):
    """Verify that the current todo has the expected description."""
    todo_id = getattr(context, 'current_todo_id', None)
    assert todo_id is not None, "A todo must be set in context"
    
    r = context.http.get(f"{context.base_url}/todos/{todo_id}", timeout=5)
    assert r.status_code == 200, f"GET /todos/{todo_id} failed: {r.status_code}, body: {r.text}"
    
    data = r.json()
    todos = extract_collection(data, "todos")
    
    if todos and len(todos) > 0:
        todo = todos[0]
    else:
        raise AssertionError(f"Todo with id {todo_id} not found in response")
    
    actual_description = todo.get("description", "")
    assert actual_description == expected_description, (
        f"Expected description '{expected_description}', got '{actual_description}'"
    )

@when('I try to change todo {id} s description to {new_description}')
def step_try_change_nonexistent_todo_description(context, id, new_description):
    """Attempt to change the description of a nonexistent todo."""
    payload = {"description": new_description}
    r = context.http.post(f"{context.base_url}/todos/{id}", json=payload, timeout=5)
    context.last_response = r
