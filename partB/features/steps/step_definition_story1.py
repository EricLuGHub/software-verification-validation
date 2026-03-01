"""

As a McGill student, I want to create categories for each course.

"""

from behave import when, then

@when('I create a category named "{name}"')
def step_create_category(context, name):
    payload = {"title": name}
    r = context.http.post(f"{context.base_url}/categories", json=payload, timeout=5)
    context.last_response = r
    assert r.status_code == 201, f"Expected 201, got {r.status_code}, body: {r.text}"

@then('the category "{name}" should be created successfully')
def step_verify_category(context, name):
    r = context.http.get(f"{context.base_url}/categories", params={"title": name}, timeout=5)
    assert r.status_code == 200, f"GET /categories failed: {r.status_code}, body: {r.text}"

    data = r.json()

    items = []
    if isinstance(data, dict):
        items = data.get("categories") or data.get("category") or data.get("items") or []
        if isinstance(items, dict):
            items = [items]
    elif isinstance(data, list):
        items = data

    found = any((isinstance(x, dict) and x.get("title") == name) for x in items)
    assert found, f'Category "{name}" not found in response: {data}'

