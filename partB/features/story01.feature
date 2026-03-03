Feature:
    As a McGill student, I want to create categories for each course.
    

    Background:
        Given the API service is running

    # Normal flow

    Scenario Outline: Create a category for a course
        When I create a category named <title>
        Then the category <title> should be created successfully
    
    Examples:
        | title     |
        | COMP 310  |
        | COMP 250  |
        | COMP 202  |

    
    # Alternate flow

    Scenario Outline: Rename an old category to a new course name
        Given a category named <old_title> exists
        When I rename category <old_title> to <new_title>
        Then the category <new_title> should be created successfully

    Examples:
        | old_title | new_title       |
        | COMP 310  | COMP 310 - OS   |
        | COMP 250  | COMP 250 - Intro|
    
    # Error flow

    Scenario: Create a category with empty name
        When I create a category with an empty name
        Then the API should return an error indicating that the category name cannot be empty
    