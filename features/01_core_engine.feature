Feature: Core Engine and Schema Parsing
  As a developer
  I want the system to correctly interpret JSON Schema rules
  So that the generated data is structurally valid

  Scenario: Generation of a simple JSON object
    Given I have a valid schema file "user_schema.json"
    When I run the generation command using this schema
    Then the system returns a valid JSON object
    And the object keys correspond to the schema properties

  Scenario: Respecting Numerical Constraints
    Given the schema defines a property "age" of type integer
    And the property "age" has minimum 18 and maximum 99
    When I generate the data
    Then the value of the field "age" is an integer between 18 and 99 inclusive

  Scenario: Generation of correct email formats
    Given the schema defines a property "contact" with format "email"
    When I generate the data
    Then the value of the field "contact" respects the standard regex for emails

  Scenario: Generation of a list with guaranteed minimum length
    Given the schema defines a property "tags" of type array
    And the property has minItems set to 5
    When I generate the data
    Then the array "tags" in the resulting JSON contains at least 5 elements

  Scenario: Generation of complex and nested objects
    Given the schema contains an object "address" nested inside the main object
    When I generate the data
    Then the JSON output contains the key "address"
    And the value of "address" is an object with its own sub-properties populated

  Scenario: Selection of values from an enumerated list (Enum)
    Given the schema has a field "status" with enum ["active", "suspended", "deleted"]
    When I generate the data
    Then the value of the field "status" is exclusively one of the three allowed strings