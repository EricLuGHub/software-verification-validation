Feature: Listing incomplete TODOs
  As an ECSE 429 student,
  I want to be able to list out all incomplete TODOs
  to keep track of what still needs to be done.

	Background:
		Given the API service is running
    And the default objects have been removed


  # Normal flow

	Scenario Outline: Normal Flow: User can list only incomplete TODOs
    Given some todo with title <title_a> exists marked as complete
    And some todo with title <title_b> exists marked as incomplete
    When I list every todo marked as incomplete
    Then todo <title_b> should be returned
    But todo <title_a> should not be returned
  Examples:
      | title_a | title_b |
      | Todo1   | Todo2   |
      | TaskA   | TaskB   |

  # Alternate flow

  Scenario Outline: Alternate Flow: User can list only incomplete TODOs even when there are none
    Given some todo with title <title> exists marked as complete
    When I list every todo marked as incomplete
    Then nothing should be returned
  Examples:
      | title  |
      | Todo1  |
      | Todo2  |


  # Error flow

  Scenario Outline: Error Flow: User cannot filter TODOs by an invalid status type
    When I list every todo marked as <invalid_status>
    Then the request should be refused
  Examples:
      | invalid_status |
      | done           |
      | incomplete     |
