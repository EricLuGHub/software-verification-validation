Feature: Creating projects
  As an ECSE 429 student,
  I want to create a project
  to keep track of the deliverables
  for one part of the term project.

	Background:
		Given the application is running


	# Normal flow

	Scenario Outline: User can create a project with a title
    When some project is created with title <title>
    Then some project <id> should be returned
    And project <id> should exist with title <title>

  Scenario Outline: User can link a todo to a project
    Given some project <project_id> exists
    And some todo <todo_id> exists
    When todo <todo_id> is made a task of project <project_id>
    Then the request should be accepted
    And todo <todo_id> should be a task of project <project_id>


  # Alternate flow

  Scenario Outline: User can create a project with no extra parameters
    When some project is created
    Then some project <id> should be returned
    And project <id> should exist


  # Error flow

  Scenario Outline: User cannot create a project while specifying an ID
    Given some project <id> does not exist
    When some project is created with id <id>
    Then the request should be refused
    And project <id> should not exist
