Feature:
    As a McGill student, I want to create categories for each course.
    
    Scenario: Create a category for a course
        Given the API service is running
        When I create a category named "COMP 310"
        Then the category "COMP 310" should be created successfully