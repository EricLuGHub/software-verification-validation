Feature: Completing TODOs
  As an ECSE 429 student,
  I want to be able to mark a TODO as complete
  to keep track of what's already been done.

	Background:
		Given the API service is running


	# Normal flow

  Scenario Outline: Normal Flow: User can mark a TODO as complete
    Given a todo with title <todo_title> exists
    When I mark todo <todo_title> as complete
    Then todo <todo_title> should be marked as complete
  
  Examples:
      | todo_title |
      | Todo1      |
      | Todo2      |


  # Alternate flow

  Scenario Outline: Alternate Flow: User can create a TODO already marked as complete
    When I create a todo with title <todo_title> and mark as complete
    Then the todo <todo_title> should be returned
    And todo <todo_title> should exist with the correct id
    And todo <todo_title> should be marked as complete

  Examples:
      | todo_title |
      | Todo1      |
      | Todo2      |

  # Error flow

  Scenario Outline: Error Flow: User cannot mark a nonexistent TODO as complete
    Given some todo with id <id> does not exist
    When I make todo with id <id> marked as complete
    Then the request should be refused
    And todo with id <id> should not exist
  Examples:
      | id  |
      | 999 |
      | 456 |
