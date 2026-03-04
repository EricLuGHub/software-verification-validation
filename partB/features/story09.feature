Feature: Deleting taskof relationships
  As a user,
  I want to delete a taskof relationship
  I accidentally created.

	Background:
		Given the application is running


  # Normal flow

	Scenario Outline: User can delete a taskof relationship from the task's side
    Given some project exists
    And some todo is a task of that project
    When I delete the relationship between the two from the task's side
    Then the request should be accepted
    And the relationship should no longer exist


  # Alternate flow

  Scenario Outline: User can delete a taskof relationship from the project's side
    Given some project exists
    And some todo is a task of that project
    When I delete the relationship between the two from the project's side
    Then the request should be accepted
    And the relationship should no longer exist


  # Error flow

  Scenario Outline: User cannot delete a nonexistent taskof relationship from the task's side
    Given some project exists
    And some todo exists
    And a taskof relationship between the two does not exist
    When I delete the relationship between the two from the task's side
    Then the request should be refused

  Scenario Outline: User cannot delete a nonexistent taskof relationship from the project's side
    Given some project exists
    And some todo exists
    And a taskof relationship between the two does not exist
    When I delete the relationship between the two from the project's side
    Then the request should be refused
