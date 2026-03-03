Feature: Creating projects
  As an ECSE 429 student,
  I want to create a project
  to keep track of the deliverables
  for one part of the term project.

	Background:
		Given the API service is running


	# Normal flow

	Scenario Outline: User can create a project with a title
    When I create some project with title <title>
    Then the project <title> should be created successfully

  Examples:
    | title          |
    | Project1       |
    | Project2       |


  # Alternate flow

  Scenario Outline: User can rename an old project project into a new project name
    Given some project <old_title> exists
    When I rename project <old_title> to <new_title>
    Then the project <new_title> should be created successfully
  
  Examples:
    | old_title | new_title |
    | OldProj1  | Project1  |
    | OldProj2  | Project2  |
    

  # Error flow

  Scenario Outline: User cannot create a project while specifying an ID
    Given some project <id> does not exist
    When I create some project with id <id>
    Then the request should be refused
    And project <id> should not exist

  Examples:
    | id  |
    | 999 |
    | 456 |
