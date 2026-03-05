Feature: Changing titles
  As a user,
  I want to change the title of a project
  to make it consistent with the other projects.

  Background:
		Given the API service is running


  # Normal flow

	Scenario Outline: Normal Flow: User can change a project title through a POST request
    Given some project <title> exists with description <description>
    When I change project <title> title to <title_b> through a POST request
    Then its title should be <title_b>
    And nothing else should change for project <title_b>
  
  Examples:
      | title     | description       | title_b   |
      | Project1  | First project     | ProjectA  |
      | Project2  | Second project    | ProjectB  |


  # Alternate flow

  Scenario Outline: Alternate Flow: User can change a project title through a PUT request
    Given some project <title> exists with description <description>
    When I change project <title> title to <title_b> through a PUT request
    Then its title should be <title_b>
    And nothing else should change for project <title_b>

  Examples:
      | title     | description       | title_b   |
      | Project1  | First project     | ProjectA  |
      | Project2  | Second project    | ProjectB  |


  # Error flow

  Scenario Outline: Error Flow: User cannot change the title of a nonexistent project through a POST request
    Given some project <project> does not exist
    When I change project <project> title to <title> through a POST request
    Then the request should be refused
    And project titled <project> should not exist

  Examples:
      | project   | title     |
      | ProjectX  | NewTitle1 |
      | ProjectY  | NewTitle2 |

  Scenario Outline: Error Flow: User cannot change the title of a nonexistent project through a PUT request
    Given some project <project> does not exist
    When I change project <project> title to <title> through a PUT request
    Then the request should be refused
    And project titled <project> should not exist

  Examples:
      | project   | title    |
      | ProjectX  | NewTitle1|
      | ProjectY  | NewTitle2|
