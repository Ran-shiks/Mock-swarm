from behave.api.pending_step import StepNotImplementedError
from behave import given, when, then

# cli_steps.py

@given(u'a file "./schemas/order.json" exists on the local disk')
def step_impl(context):
    raise StepNotImplementedError(u'Given a file "./schemas/order.json" exists on the local disk')
@when(u'I run "mockgen generate --schema ./schemas/order.json"')
def step_impl(context):
    raise StepNotImplementedError(u'When I run "mockgen generate --schema ./schemas/order.json"')
@then(u'the system correctly reads the file and does not return a "File not found" error')
def step_impl(context):
    raise StepNotImplementedError(u'Then the system correctly reads the file and does not return a "File not found" error')


@given(u'I want to save the generated data')
def step_impl(context):
    raise StepNotImplementedError(u'Given I want to save the generated data')
@when(u'I run the command with the option "--out ./output/data.json"')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the command with the option "--out ./output/data.json"')
@then(u'a file "data.json" is created in the specified folder')
def step_impl(context):
    raise StepNotImplementedError(u'Then a file "data.json" is created in the specified folder')
@then(u'the file contains the generated JSON data')
def step_impl(context):
    raise StepNotImplementedError(u'Then the file contains the generated JSON data')


@given(u'I need a voluminous dataset')
def step_impl(context):
    raise StepNotImplementedError(u'Given I need a voluminous dataset')
@when(u'I run the command with the option "--count 50"')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the command with the option "--count 50"')
@then(u'the output is a JSON array containing exactly 50 objects')
def step_impl(context):
    raise StepNotImplementedError(u'Then the output is a JSON array containing exactly 50 objects')


@given(u'I want to analyze the internal behavior of the tool')
def step_impl(context):
    raise StepNotImplementedError(u'Given I want to analyze the internal behavior of the tool')
@when(u'I run the command with the "--verbose" flag')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the command with the "--verbose" flag')
@then(u'the console shows details of the request sent to the LLM and response times')
def step_impl(context):
    raise StepNotImplementedError(u'Then the console shows details of the request sent to the LLM and response times')
