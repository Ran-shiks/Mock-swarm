@skip
Feature: AI Integration
  As a user
  I want to use an LLM to generate data
  So that the data is semantically realistic and contextual

  Scenario: Contextual generation via semantic prompt
    Given I have a schema for "product_review"
    And I provide the prompt "Customer very disappointed with shipping"
    When I run the generation in AI mode
    Then the field "comment" in the JSON contains text expressing dissatisfaction with shipping

  Scenario: AI Provider selection via configuration
    Given I have set the environment variable LLM_PROVIDER to "openai"
    When I run the generation command with the --ai flag
    Then the system makes the API call to the OpenAI endpoints

  Scenario: Handling AI API failure (Fallback)
    Given AI mode is active
    But the LLM service is unreachable or times out
    When the system attempts to generate data
    Then the system automatically switches to algorithmic generation
    And a warning message is shown to the user

  Scenario: Sending minimized schema to LLM (Token Optimization)
    Given I have a very verbose JSON schema with long descriptions
    When the system prepares the request for the LLM
    Then the schema is minified by removing spaces and non-essential metadata before sending