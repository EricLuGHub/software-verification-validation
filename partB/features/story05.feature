Feature: Creating taskof relationships
  As an ECSE 429 student,
  I want to make a TODO a task of a project
  to group the project’s deliverables together.

  Background:
		Given the API service is running


  # Normal flow

	Scenario Outline: Normal Flow: User can create a taskof relationship between an already existing todo and an already existing project
    Given some project <project_title> exists
    And some todo <todo_title> exists
    When I make the todo <todo_title> a task of project <project_title>
  Then the taskof relationship request should be accepted
    And the todo <todo_title> should be a task of project <project_title>
  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | TaskA      |


  # Alternate flow

  Scenario Outline: Alternate Flow: User can create a taskof relationship while creating a todo
    Given some project <project_title> exists
    When I create some todo <todo_title> as a task of project <project_title>
    Then the taskof relationship request should be accepted
    And the todo should be a task of that project
  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | TaskA      |


  # Error flow

  Scenario Outline: Error Flow: User cannot create a taskof relationship between a todo and a nonexistent project
    Given some todo <todo_title> exists
    And some project with id <id> does not exist
    When I make the todo <todo_title> a task of project <id>
    Then the request should be refused
  Examples:
      | todo_title | id  |
      | Todo1      | 999 |
      | TaskA      | 456 |
