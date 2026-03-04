Feature: Deleting taskof relationships
  As a user,
  I want to delete a taskof relationship
  I accidentally created.

	Background:
    Given the API service is running


  # Normal flow

	Scenario Outline: User can delete a taskof relationship from the task's side
  Given some relationship project with title <project_title> exists
    And some todo with title <todo_title> exists
    And todo with title <todo_title> is a task of that project
    When I delete the relationship between the two from the task's side
    Then the request should be accepted
    And the relationship should no longer exist
    Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | Todo2      |

  # Alternate flow

  Scenario Outline: User can delete a taskof relationship from the project's side
    Given some relationship project with title <project_title> exists
    And some todo is a task of project <project_title>
    When I delete the relationship between the two from the project's side
    Then the request should be accepted
    And the relationship should no longer exist
    Examples:
      | project_title |
      | Project1      |
      | Project2      |


  # Error flow

  Scenario Outline: User cannot delete a nonexistent taskof relationship from the task's side
    Given some relationship project with title <project_title> exists
    And some todo with title <todo_title> exists
    And a taskof relationship between the two does not exist
    When I delete the relationship between the two from the task's side
    Then the request should be refused

  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | Todo2      |
    

  Scenario Outline: User cannot delete a nonexistent taskof relationship from the project's side
    Given some relationship project with title <project_title> exists
    And some todo with title <todo_title> exists
    And a taskof relationship between the two does not exist
    When I delete the relationship between the two from the project's side
    Then the request should be refused
  
  Examples:
      | project_title | todo_title |
      | Project1      | Todo1      |
      | Project2      | Todo2      |