"""

As a McGill student, I want to create categories for each course.

"""

from behave import when, then, given
from step_utils import extract_collection, find_by_title

@when('I create a category named {name}')
def step_create_category(context, name):
    payload = {"title": name}
    r = context.http.post(f"{context.base_url}/categories", json=payload, timeout=5)
    context.last_response = r
    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"

@then('the category {name} should be created successfully')
def step_verify_category(context, name):
    r = context.http.get(f"{context.base_url}/categories", params={"title": name}, timeout=5)
    assert r.status_code == 200, f"GET /categories failed: {r.status_code}, body: {r.text}"

    data = r.json()
    items = extract_collection(data, "categories")
    found = any((isinstance(x, dict) and x.get("title") == name) for x in items)
    assert found, f'Category "{name}" not found in response: {data}'

@given('a category named {name} exists')
def step_category_exists(context, name):

    r = context.http.get(f"{context.base_url}/categories", params={"title": name}, timeout=5)
    assert r.status_code == 200, f"GET /categories failed: {r.status_code}, body: {r.text}"

    data = r.json()

    for item in data.get("categories", []):
        if item.get("title") == name:
            return

    payload = {"title": name}
    r = context.http.post(f"{context.base_url}/categories", json=payload, timeout=5)
    assert r.status_code == 201, f"Failed to create category '{name}': {r.status_code}, body: {r.text}"

@when('I rename category {old_name} to {new_name}')
def step_rename_category(context, old_name, new_name):
    r = context.http.get(f"{context.base_url}/categories", params={"title": old_name}, timeout=5)
    assert r.status_code == 200, f"GET /categories failed: {r.status_code}, body: {r.text}"

    data = r.json()
    categories = extract_collection(data, "categories")
    category = find_by_title(categories, old_name)
    category_id = category.get("id") if category else None

    if not category_id:
        raise AssertionError(f"Category '{old_name}' not found")
    
    payload = {"title": new_name}
    r = context.http.put(f"{context.base_url}/categories/{category_id}", json=payload, timeout=5)
    assert r.status_code == 200, f"Failed to rename category '{old_name}' to '{new_name}': {r.status_code}, body: {r.text}"


@when('I create a category with an empty name')
def step_create_category_empty_name(context):
    payload = {}
    context.last_response = context.http.post(
        f"{context.base_url}/categories", json=payload, timeout=5
    )

@then('the API should return an error indicating that the category name cannot be empty')
def step_verify_empty_name_error(context):
    r = context.last_response
    assert r.status_code == 400, f"Expected validation error, got {r.status_code}, body: {r.text}"