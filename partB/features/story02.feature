Feature: Listing tasks of a project
  As an ECSE 429 student,
  I want to list all the TODOs related to a project
  to know what deliverables are expected.

  Background:
    Given the API service is running


  # Normal flow

	Scenario Outline: Normal Flow: User can list tasks of a project
    Given some project <project_title> exists
    And some todo <todo_title> is a task of that project
    When I list tasks of that project
    Then todo <todo_title> should be returned
  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | TaskA      |


  # Alternate flow

  Scenario Outline: Alternate Flow: User can list tasks of a project, even when there are none
    Given some project <project_title> with no tasks exists
    When I list tasks of that project
    Then the request should be accepted
    And nothing should be returned
  Examples:
      | project_title |
      | Project1      |
      | Project2      |


  # Error flow

  Scenario Outline: Error Flow: User cannot list tasks of a nonexistent project
    Given some project <project> does not exist
    When I list tasks of project <project>
    Then the request should be refused
  Examples:
      | project  |
      | ProjectX |
      | ProjectY |
