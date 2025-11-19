Feature: CLI Interface
  As a terminal user
  I want to control the generator via flags and commands
  So that I can integrate it into my development workflow

  Scenario: Reading schema from local path
    Given a file "./schemas/order.json" exists on the local disk
    When I run "mockgen generate --schema ./schemas/order.json"
    Then the system correctly reads the file and does not return a "File not found" error

  Scenario: Saving output to disk
    Given I want to save the generated data
    When I run the command with the option "--out ./output/data.json"
    Then a file "data.json" is created in the specified folder
    And the file contains the generated JSON data

  Scenario: Multiple record generation
    Given I need a voluminous dataset
    When I run the command with the option "--count 50"
    Then the output is a JSON array containing exactly 50 objects

  Scenario: Viewing debug logs
    Given I want to analyze the internal behavior of the tool
    When I run the command with the "--verbose" flag
    Then the console shows details of the request sent to the LLM and response times