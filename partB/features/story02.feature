Feature: Listing tasks of a project
  As an ECSE 429 student,
  I want to list all the TODOs related to a project
  to know what deliverables are expected.

  Background:
    Given the API service is running


  # Normal flow

	Scenario Outline: User can list tasks of a project
    Given some project <project_title> exists
    And some todo <todo_title> a task of that project
    When I list tasks of that project
    Then todo <todo_title> should be returned
  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | TaskA      |


  # Alternate flow

  Scenario Outline: User can list tasks of a project, even when there are none
    Given some project <project_title> has no tasks
    And some todo <project_title> exists
    When I list tasks of project <project_title>
    Then the request is accepted
    But nothing is returned
  Examples:
      | project_title |
      | Project1      |
      | Project2      |


  # Error flow

  Scenario Outline: User cannot list tasks of a nonexistent project
    Given some project <project> does not exist
    When I list tasks of project <project>
    Then the request is refused
  Examples:
      | project  |
      | ProjectX |
      | ProjectY |
