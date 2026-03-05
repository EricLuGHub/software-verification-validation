Feature: Changing descriptions
  As a McGill student,
  I want to change the due date in the description of a TODO
  since I was allowed an extension.

  Background:
		Given the application is running


  # Normal flow

	Scenario Outline: User can change a TODO's description
    Given some todo <todo_title> exists with description <description_a>
    When I change todo <todo_title> description to <description_b>
    Then the request should be accepted
    And it should have description <description_b>


  # Alternate flow

  Scenario Outline: User can add a description to a TODO without one
    Given some todo <todo_title> exists with description <description_a>
    When I change its description to <description_b>
    Then the request should be accepted
    And it should have description <description_b>
  
  Examples:
      | todo_title | description_a       | description_b       | description         |
      | Todo1      | Due next week       | Due next month      | Due next week       |
      | TaskA      |                     | Due tomorrow        | Due today           |

  # Error flow

  Scenario Outline: User cannot change the description of a nonexistent TODO
    Given some todo with id <id> does not exist
    When I change todo <id> s description to <description>
    Then the request should be refused
    And todo with id <id> should not exist
  Examples:
      | id  | description         |
      | 999 | Due next week       |
      | 888 | Due next month      |
