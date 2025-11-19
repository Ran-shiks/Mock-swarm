Feature: Reliability and Validation
  As a QA Engineer
  I want the system to be robust and predictable
  So that my tests are reliable

  Scenario: Data reproducibility via seed
    Given I set the seed to "12345"
    When I run the generation twice consecutively with the same schema
    Then the first JSON output is identical character-by-character to the second JSON output

  Scenario: AI output validation
    Given the LLM has generated a JSON response
    When the system receives the response
    Then it verifies that the JSON respects the original schema
    And if it is not valid, it discards the result or attempts a repair

  Scenario: Reporting invalid schema
    Given I provide a JSON file that contains syntax errors
    When I attempt to run the generation
    Then the system terminates with an error code
    And prints a clear message indicating the line or type of error in the JSON