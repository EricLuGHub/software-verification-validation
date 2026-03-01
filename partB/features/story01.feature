Feature:
    As a McGill student, I want to create categories for each course.
    
    # Normal flow
    Scenario: Create a category for a course
        Given the API service is running
        When I create a category named "COMP 310"
        Then the category "COMP 310" should be created successfully

    
    # Alternate flow

    Scenario: Rename an old category to a new course name
        Given the API service is running
        And a category named "COMP 310" exists
        When I create a category named "COMP 310 - OS"
        Then the category "COMP 310 - OS" should be created successfully