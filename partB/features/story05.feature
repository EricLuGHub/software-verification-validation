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
    Then the request should be accepted
    And the todo <todo_title> should be a task of project <project_title>
  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | TaskA      |


  # Alternate flow

  Scenario Outline: Alternate Flow: User can create a taskof relationship while creating a todo
    Given some project exists
    When I create some todo as a task of that project
    Then the request should be accepted
    And the todo should be a task of that project


  # Error flow

  Scenario Outline: Error Flow: User cannot create a taskof relationship between a todo and a nonexistent project
    Given some todo exists
    And some project with id <id> does not exist
    When I make the todo a task of project <id>
    Then the request should be refused

  Scenario Outline: Error Flow: User cannot create an already existing taskof relationship
    Given some project exists
    And some todo is a task of that project
    When I make the todo a task of that project
    Then the request should be refused
    And nothing should change
