from behave.api.pending_step import StepNotImplementedError
from behave import given, when, then

# advanced_output_steps.py

@given(u'I have a flat schema (without complex nested objects)')
def step_impl(context):
    raise StepNotImplementedError(u'Given I have a flat schema (without complex nested objects)')
@when(u'I run the command with "--format csv"')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the command with "--format csv"')
@then(u'the output is formatted as comma-separated text with headers')
def step_impl(context):
    raise StepNotImplementedError(u'Then the output is formatted as comma-separated text with headers')


@given(u'I am generating a large number of records')
def step_impl(context):
    raise StepNotImplementedError(u'Given I am generating a large number of records')
@when(u'I run the command with "--format ndjson"')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the command with "--format ndjson"')
@then(u'each JSON object is printed on a new line as it is generated')
def step_impl(context):
    raise StepNotImplementedError(u'Then each JSON object is printed on a new line as it is generated')


@given(u'I am writing a test script in Node.js')
def step_impl(context):
    raise StepNotImplementedError(u'Given I am writing a test script in Node.js')
@when(u'I import the library and call "MockGen.generate(schema)"')
def step_impl(context):
    raise StepNotImplementedError(u'When I import the library and call "MockGen.generate(schema)"')
@then(u'the function returns a Promise that resolves with the data object')
def step_impl(context):
    raise StepNotImplementedError(u'Then the function returns a Promise that resolves with the data object')