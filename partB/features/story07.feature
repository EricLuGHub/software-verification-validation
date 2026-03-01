Feature: Completing TODOs
  As an ECSE 429 student,
  I want to be able to mark a TODO as complete
  to keep track of what's already been done.

	Background:
		Given the application is running


	# Normal flow

	Scenario Outline: User can mark a TODO as complete
    Given some todo <id> exists
    When I make todo <id> marked as complete
    Then todo <id> should be marked as complete


  # Alternate flow

  Scenario Outline: User can create a TODO already marked as complete
    When I create some todo marked as complete
    Then some todo <id> should be returned
    And todo <id> should exist
    And todo <id> should be marked as complete


  # Error flow

  Scenario Outline: User cannot mark a nonexistent TODO as complete
    Given some todo <id> does not exist
    When I make todo <id> marked as complete
    Then the request should be refused
    And todo <id> should not exist
