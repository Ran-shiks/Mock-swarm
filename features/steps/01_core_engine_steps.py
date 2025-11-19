
from behave.api.pending_step import StepNotImplementedError
from behave import given, when, then

# Basic Generation Steps

@given(u'I have a valid schema file "user_schema.json"')
def step_impl(context):
    raise StepNotImplementedError(u'Given I have a valid schema file "user_schema.json"')
@when(u'I run the generation command using this schema')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the generation command using this schema')
@then(u'the system returns a valid JSON object')
def step_impl(context):
    raise StepNotImplementedError(u'Then the system returns a valid JSON object')
@then(u'the object keys correspond to the schema properties')
def step_impl(context):
    raise StepNotImplementedError(u'Then the object keys correspond to the schema properties')


@given(u'the schema defines a property "age" of type integer')
def step_impl(context):
    raise StepNotImplementedError(u'Given the schema defines a property "age" of type integer')
@given(u'the property "age" has minimum 18 and maximum 99')
def step_impl(context):
    raise StepNotImplementedError(u'Given the property "age" has minimum 18 and maximum 99')
@when(u'I generate the data')
def step_impl(context):
    raise StepNotImplementedError(u'When I generate the data')
@then(u'the value of the field "age" is an integer between 18 and 99 inclusive')
def step_impl(context):
    raise StepNotImplementedError(u'Then the value of the field "age" is an integer between 18 and 99 inclusive')


@given(u'the schema defines a property "contact" with format "email"')
def step_impl(context):
    raise StepNotImplementedError(u'Given the schema defines a property "contact" with format "email"')
@then(u'the value of the field "contact" respects the standard regex for emails')
def step_impl(context):
    raise StepNotImplementedError(u'Then the value of the field "contact" respects the standard regex for emails')


@given(u'the schema defines a property "tags" of type array')
def step_impl(context):
    raise StepNotImplementedError(u'Given the schema defines a property "tags" of type array')
@given(u'the property has minItems set to 5')
def step_impl(context):
    raise StepNotImplementedError(u'Given the property has minItems set to 5')
@then(u'the array "tags" in the resulting JSON contains at least 5 elements')
def step_impl(context):
    raise StepNotImplementedError(u'Then the array "tags" in the resulting JSON contains at least 5 elements')


@given(u'the schema contains an object "address" nested inside the main object')
def step_impl(context):
    raise StepNotImplementedError(u'Given the schema contains an object "address" nested inside the main object')
@then(u'the JSON output contains the key "address"')
def step_impl(context):
    raise StepNotImplementedError(u'Then the JSON output contains the key "address"')
@then(u'the value of "address" is an object with its own sub-properties populated')
def step_impl(context):
    raise StepNotImplementedError(u'Then the value of "address" is an object with its own sub-properties populated')


@given(u'the schema has a field "status" with enum ["active", "suspended", "deleted"]')
def step_impl(context):
    raise StepNotImplementedError(u'Given the schema has a field "status" with enum ["active", "suspended", "deleted"]')
@then(u'the value of the field "status" is exclusively one of the three allowed strings')
def step_impl(context):
    raise StepNotImplementedError(u'Then the value of the field "status" is exclusively one of the three allowed strings')
