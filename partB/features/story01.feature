Feature:
    As a McGill student, I want to create categories for each course.
    

    Background:
        Given the API service is running

    # Normal flow

    Scenario: Create a category for a course
        When I create a category named "COMP 310"
        Then the category "COMP 310" should be created successfully

    
    # Alternate flow

    Scenario: Rename an old category to a new course name
        Given a category named "COMP 310" exists
        When I rename "COMP 310" to "COMP 310 - OS"
        Then the category "COMP 310 - OS" should be created successfully
    
    # Error flow

    Scenario: Create a category with empty name
        When I create a category with an empty name
        Then the API should return an error indicating that the category name cannot be empty