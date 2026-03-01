Feature: Listing incomplete TODOs
  As an ECSE 429 student,
  I want to be able to list out all incomplete TODOs
  to keep track of what still needs to be done.

	Background:
		Given the application is running
    And the default objects have been removed


  # Normal flow

	Scenario Outline: User can list only incomplete TODOs
    Given some todo <id_a> exists marked as complete
    And some todo <id_b> exists marked as incomplete
    When I list every todo marked as incomplete
    Then todo <id_b> should be returned
    But todo <id_a> should not be returned


  # Alternate flow

  Scenario Outline: User can list only incomplete TODOs even when there are none
    Given some todo <id_a> exists marked as complete
    When I list every todo marked as incomplete
    Then nothing should be returned


  # Error flow

  Scenario Outline: User cannot filter TODOs by an invalid status type
    When I list every todo marked as <invalid_status>
    Then the request should be refused
