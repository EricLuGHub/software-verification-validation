Feature: Deleting taskof relationships
  As a user,
  I want to delete a TODO
  to clear up future requests.

	Background:
		Given the API service is running


  # Normal flow

	Scenario Outline: User can delete a TODO
    Given some todo <todo> exists
    When I delete todo <todo>
    Then the request should be accepted
    And todo with title <todo> should not exist
  Examples:
      | todo   |
      | Todo1  |
      | TaskA  |


  # Alternate flow

  Scenario Outline: User can delete a TODO with existing taskof relationships
    Given some project <project> exists
    And some todo <todo> is a task of that project
    When I delete todo <todo>
    Then the request should be accepted
    And todo with title <todo> should not exist
    And todo <todo> should not be a task of <project>
  Examples:
      | project  | todo   |
      | Project1 | Todo1  |
      | Project2 | TaskA  |


  # Error flow

  Scenario Outline: User cannot delete a nonexistent TODO
    Given some todo <todo> does not exist
    When I delete todo <todo>
    Then the request should be refused
    And todo with title <todo> should not exist
  Examples:
      | todo   |
      | Todo999 |
      | Task456 |
