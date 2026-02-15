import requests
from pathlib import Path
import sys

# Add parent directory to path to import test_helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_helpers import (
    HOST,
    PROJECTS,
    todo_server,
    assert_has_common_headers,
    generate_title,
    create_project,
    create_todo,
    create_category,
    require_created_id,
    assert_subset,
)


# =====================================
# Additional Project Endpoint Tests
# =====================================

def test_get_projects_filter_by_id_query(todo_server):
    """Test GET /projects?id=X returns only that project"""
    title = generate_title("project-id-filter")
    create_resp = create_project(name=title)
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}?id={project_id}", timeout=3)
    assert r.status_code == 200
    body = r.json()
    
    assert "projects" in body
    assert len(body["projects"]) == 1
    assert body["projects"][0]["id"] == project_id


def test_get_projects_filter_by_id_nonexistent(todo_server):
    """Test GET /projects?id=X with nonexistent ID returns empty list"""
    r = requests.get(f"{HOST}{PROJECTS}?id=0", timeout=3)
    assert r.status_code == 200
    body = r.json()
    
    assert body["projects"] == []


def test_get_projects_filter_ignores_invalid_params(todo_server):
    """Test GET /projects ignores invalid query parameters"""
    title = generate_title("project-invalid-param")
    create_resp = create_project(name=title)
    project_id = require_created_id(create_resp)

    r = requests.get(f"{HOST}{PROJECTS}?asdfajksdlf=test&id={project_id}", timeout=3)
    assert r.status_code == 200
    body = r.json()
    
    assert any(p["id"] == project_id for p in body["projects"])


def test_get_projects_filter_by_title(todo_server):
    """Test GET /projects?title=X returns projects matching title"""
    title = generate_title("project-title-filter")
    create_resp = create_project(name=title)
    project_id = require_created_id(create_resp)

    # Test exact title match
    r = requests.get(f"{HOST}{PROJECTS}?title={requests.utils.quote(title)}", timeout=3)
    assert r.status_code == 200
    body = r.json()
    
    assert any(p["title"] == title for p in body["projects"])


def test_post_project_missing_title(todo_server):
    """Test POST /projects without title returns 400"""
    payload = {
        "description": "test project"
    }
    r = requests.post(f"{HOST}{PROJECTS}", json=payload, timeout=3)
    assert r.status_code == 400
    
    body = r.json()
    assert "errorMessages" in body


def test_post_project_with_invalid_field(todo_server):
    """Test POST /projects with invalid field returns error"""
    payload = {
        "title": generate_title("project"),
        "invalidField": "test"
    }
    r = requests.post(f"{HOST}{PROJECTS}", json=payload, timeout=3)
    assert r.status_code == 400
    
    body = r.json()
    assert "errorMessages" in body
    assert "Could not find field: invalidField" in str(body["errorMessages"])


def test_post_project_with_id_in_payload(todo_server):
    """Test POST /projects with id in payload returns error"""
    payload = {
        "id": "999",
        "title": generate_title("project"),
        "description": "test"
    }
    r = requests.post(f"{HOST}{PROJECTS}", json=payload, timeout=3)
    assert r.status_code == 400
    
    body = r.json()
    assert "errorMessages" in body


def test_put_project_by_id_with_missing_title(todo_server):
    """Test PUT /projects/:id with missing title returns 400"""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "description": generate_title("amend-project-put-desc")
    }
    r = requests.put(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 400
    
    body = r.json()
    assert "errorMessages" in body


def test_put_project_by_id_with_invalid_field(todo_server):
    """Test PUT /projects/:id with invalid field returns 400"""
    create_resp = create_project()
    project_id = require_created_id(create_resp)

    payload = {
        "title": generate_title("amend-project"),
        "invalidField": "test"
    }
    r = requests.put(f"{HOST}{PROJECTS}/{project_id}", json=payload, timeout=3)
    assert r.status_code == 400


def test_put_project_nonexistent_id(todo_server):
    """Test PUT /projects/0 with nonexistent ID returns 404"""
    payload = {
        "title": generate_title("amend-project"),
        "description": "test"
    }
    r = requests.put(f"{HOST}{PROJECTS}/0", json=payload, timeout=3)
    assert r.status_code == 404


# =====================================
# Project Tasks Specific Tests
# =====================================

def test_get_project_tasks_specific_relationship(todo_server):
    """Test GET /projects/:id/tasks/:id - Get specific task relationship"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    # Create relationship first
    payload = {"id": todo_id}
    requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)

    # Now get the specific task relationship
    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/tasks/{todo_id}", timeout=3)
    
    # This endpoint may or may not exist, so we're documenting the behavior
    assert r.status_code in (200, 404, 405)
    if r.status_code == 200:
        body = r.json()
        assert "todos" in body or "id" in str(body)


def test_post_project_tasks_specific_relationship(todo_server):
    """Test POST /projects/:id/tasks/:id - Modify specific task relationship"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    # Create relationship first
    payload = {"id": todo_id}
    requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)

    # Try POST on specific relationship
    r = requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks/{todo_id}", json={}, timeout=3)
    
    # Document behavior
    assert r.status_code in (200, 201, 400, 404, 405)


def test_head_project_tasks_specific_relationship(todo_server):
    """Test HEAD /projects/:id/tasks/:id - Get headers for specific task"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_todo_resp = create_todo()
    todo_id = require_created_id(create_todo_resp)

    # Create relationship first
    payload = {"id": todo_id}
    requests.post(f"{HOST}{PROJECTS}/{project_id}/tasks", json=payload, timeout=3)

    # Try HEAD on specific relationship
    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/tasks/{todo_id}", timeout=3)
    
    # Document behavior
    assert r.status_code in (200, 204, 404, 405)
    if r.status_code in (200, 204):
        assert_has_common_headers(r)


def test_head_project_tasks_specific_nonexistent(todo_server):
    """Test HEAD /projects/:id/tasks/:id with nonexistent task ID"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/tasks/0", timeout=3)
    
    # Document behavior
    assert r.status_code in (404, 405)


def test_delete_project_tasks_with_nonexistent_todo(todo_server):
    """Test DELETE /projects/:id/tasks/:id with nonexistent todo returns 404"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.delete(f"{HOST}{PROJECTS}/{project_id}/tasks/0", timeout=3)
    assert r.status_code == 404


# =====================================
# Additional Query Parameter Tests
# =====================================

def test_get_projects_multiple_id_filters(todo_server):
    """Test GET /projects?id=X&id=Y behavior with multiple IDs"""
    title1 = generate_title("project-multi-1")
    title2 = generate_title("project-multi-2")
    
    create_resp1 = create_project(name=title1)
    create_resp2 = create_project(name=title2)
    project_id1 = require_created_id(create_resp1)
    project_id2 = require_created_id(create_resp2)

    # Query with multiple IDs
    r = requests.get(f"{HOST}{PROJECTS}?id={project_id1}&id={project_id2}", timeout=3)
    assert r.status_code == 200
    body = r.json()
    
    # Document behavior - may only return first or both
    assert "projects" in body


def test_post_project_with_special_characters(todo_server):
    """Test POST /projects with special characters in title"""
    title = generate_title("project") + " & special"
    r = create_project(name=title)
    
    assert r.status_code == 201
    body = r.json()
    # Special characters should be preserved
    assert "&" in body["title"]


def test_get_project_with_blank_id(todo_server):
    """Test GET /projects/ (with trailing slash but no ID)"""
    r = requests.get(f"{HOST}{PROJECTS}/", timeout=3)
    
    # Document behavior
    assert r.status_code in (200, 404)


# =====================================
# Project Categories Additional Tests
# =====================================

def test_get_project_categories_specific_relationship(todo_server):
    """Test GET /projects/:id/categories/:id - Get specific category relationship"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    # Create relationship
    payload = {"id": category_id}
    requests.post(f"{HOST}{PROJECTS}/{project_id}/categories", json=payload, timeout=3)

    # Try to get specific relationship
    r = requests.get(f"{HOST}{PROJECTS}/{project_id}/categories/{category_id}", timeout=3)
    
    assert r.status_code in (200, 404, 405)


def test_head_project_categories_specific_relationship(todo_server):
    """Test HEAD /projects/:id/categories/:id"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    create_category_resp = create_category()
    category_id = require_created_id(create_category_resp)

    # Create relationship
    payload = {"id": category_id}
    requests.post(f"{HOST}{PROJECTS}/{project_id}/categories", json=payload, timeout=3)

    # Try HEAD on specific relationship
    r = requests.head(f"{HOST}{PROJECTS}/{project_id}/categories/{category_id}", timeout=3)
    
    assert r.status_code in (200, 204, 404, 405)
    if r.status_code in (200, 204):
        assert_has_common_headers(r)


def test_delete_project_category_with_nonexistent_category(todo_server):
    """Test DELETE /projects/:id/categories/:id with nonexistent category"""
    create_project_resp = create_project()
    project_id = require_created_id(create_project_resp)

    r = requests.delete(f"{HOST}{PROJECTS}/{project_id}/categories/0", timeout=3)
    assert r.status_code == 404
