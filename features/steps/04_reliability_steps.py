from behave.api.pending_step import StepNotImplementedError
from behave import given, when, then

# reliability_steps.py

@given(u'I set the seed to "12345"')
def step_impl(context):
    raise StepNotImplementedError(u'Given I set the seed to "12345"')
@when(u'I run the generation twice consecutively with the same schema')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the generation twice consecutively with the same schema')
@then(u'the first JSON output is identical character-by-character to the second JSON output')
def step_impl(context):
    raise StepNotImplementedError(u'Then the first JSON output is identical character-by-character to the second JSON output')


@given(u'the LLM has generated a JSON response')
def step_impl(context):
    raise StepNotImplementedError(u'Given the LLM has generated a JSON response')
@when(u'the system receives the response')
def step_impl(context):
    raise StepNotImplementedError(u'When the system receives the response')
@then(u'it verifies that the JSON respects the original schema')
def step_impl(context):
    raise StepNotImplementedError(u'Then it verifies that the JSON respects the original schema')
@then(u'if it is not valid, it discards the result or attempts a repair')
def step_impl(context):
    raise StepNotImplementedError(u'Then if it is not valid, it discards the result or attempts a repair')


@given(u'I provide a JSON file that contains syntax errors')
def step_impl(context):
    raise StepNotImplementedError(u'Given I provide a JSON file that contains syntax errors')
@when(u'I attempt to run the generation')
def step_impl(context):
    raise StepNotImplementedError(u'When I attempt to run the generation')
@then(u'the system terminates with an error code')
def step_impl(context):
    raise StepNotImplementedError(u'Then the system terminates with an error code')
@then(u'prints a clear message indicating the line or type of error in the JSON')
def step_impl(context):
    raise StepNotImplementedError(u'Then prints a clear message indicating the line or type of error in the JSON')
