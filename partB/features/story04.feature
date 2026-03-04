Feature: Changing descriptions
  As a user,
  I want to delete all projects whose tasks are all marked as complete
  to clear clear up future requests.

  Background:
		Given the application is running


  # Normal flow

	Scenario Outline: User can delete all projects whose tasks are all marked as complete
    Given some project with at least one task and whose tasks are all marked as complete exists
    And some project with no tasks exists
    And some project with both complete and incomplete tasks exists
    And some project with at least one task and whose tasks are all marked as incomplete exists
    When I delete all projects whose tasks are all marked as complete
    Then the request should be accepted
    And only projects of the first and second type should no longer exist


  # Alternate flow

  Scenario Outline: User can delete all projects whose tasks are all marked as complete, even if there are no such projects
    Given some project with both complete and incomplete tasks exists
    And some project with at least one task and whose tasks are all marked as incomplete exists
    When I delete all projects whose tasks are all marked as complete
    Then the request should be accepted
    And nothing should change


  # Error flow

  Scenario Outline: User cannot
