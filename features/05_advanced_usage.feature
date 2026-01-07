Feature: Advanced Usage and Formats
  As an advanced user
  I want flexible output options
  So that I can use the data in different contexts

  Scenario: Exporting data to CSV
    Given I have a flat schema (without complex nested objects)
    When I run the command with "--format csv"
    Then the output is formatted as comma-separated text with headers

  Scenario: Streaming data in NDJSON
    Given I am generating a large number of records
    When I run the command with "--format ndjson"
    Then each JSON object is printed on a new line as it is generated

  @wip
  Scenario: Import into Node.js project (Library Usage)
    Given I am writing a test script in Node.js
    When I import the library and call "MockGen.generate(schema)"
    Then the function returns a Promise that resolves with the data object

  Scenario: Exporting data to SQL
    Given I want to populate a database table named "users"
    When I run the command with "--format sql --table-name users"
    Then the output contains valid INSERT INTO statements