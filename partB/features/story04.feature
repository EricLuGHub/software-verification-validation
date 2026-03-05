Feature: Changing titles
  As a user,
  I want to change the title of a project
  to make it consistent with the other projects.

  Background:
		Given the API service is running


  # Normal flow

	Scenario Outline: User can change a project title through a POST request
    Given some project <title_a> exists
    When I change its title to <title_b> through a POST request
    Then its title should be <title_b>
    And nothing else should change
  
  Examples:
      | title_a  | title_b  |
      | Project1 | ProjectA |
      | Project2 | ProjectB |

  # Alternate flow

  Scenario Outline: User can change a project title through a PUT request
    Given some project <title_a> exists
    When I change its title to <title_b> through a PUT request
    Then its title should be <title_b>
    And nothing else should change


  # Error flow

  Scenario Outline: User cannot change the title of a nonexistent project through a POST request
    Given some project <project> does not exist
    When I change its title to <title> through at POST request
    Then the request should be refused
    And project <project> should not exist

  Scenario Outline: User cannot change the title of a nonexistent project through a PUT request
    Given some project <project> does not exist
    When I change its title to <title> through at PUT request
    Then the request should be refused
    And project <project> should not exist
