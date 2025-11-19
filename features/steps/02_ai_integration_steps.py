from behave.api.pending_step import StepNotImplementedError
from behave import given, when, then

# AI Mode Steps

@given(u'I have a schema for "product_review"')
def step_impl(context):
    raise StepNotImplementedError(u'Given I have a schema for "product_review"')
@given(u'I provide the prompt "Customer very disappointed with shipping"')
def step_impl(context):
    raise StepNotImplementedError(u'Given I provide the prompt "Customer very disappointed with shipping"')
@when(u'I run the generation in AI mode')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the generation in AI mode')
@then(u'the field "comment" in the JSON contains text expressing dissatisfaction with shipping')
def step_impl(context):
    raise StepNotImplementedError(u'Then the field "comment" in the JSON contains text expressing dissatisfaction with shipping')


@given(u'I have set the environment variable LLM_PROVIDER to "openai"')
def step_impl(context):
    raise StepNotImplementedError(u'Given I have set the environment variable LLM_PROVIDER to "openai"')
@when(u'I run the generation command with the --ai flag')
def step_impl(context):
    raise StepNotImplementedError(u'When I run the generation command with the --ai flag')
@then(u'the system makes the API call to the OpenAI endpoints')
def step_impl(context):
    raise StepNotImplementedError(u'Then the system makes the API call to the OpenAI endpoints')


@given(u'AI mode is active')
def step_impl(context):
    raise StepNotImplementedError(u'Given AI mode is active')
@given(u'the LLM service is unreachable or times out')
def step_impl(context):
    raise StepNotImplementedError(u'Given the LLM service is unreachable or times out')
@when(u'the system attempts to generate data')
def step_impl(context):
    raise StepNotImplementedError(u'When the system attempts to generate data')
@then(u'the system automatically switches to algorithmic generation')
def step_impl(context):
    raise StepNotImplementedError(u'Then the system automatically switches to algorithmic generation')
@then(u'a warning message is shown to the user')
def step_impl(context):
    raise StepNotImplementedError(u'Then a warning message is shown to the user')


@given(u'I have a very verbose JSON schema with long descriptions')
def step_impl(context):
    raise StepNotImplementedError(u'Given I have a very verbose JSON schema with long descriptions')
@when(u'the system prepares the request for the LLM')
def step_impl(context):
    raise StepNotImplementedError(u'When the system prepares the request for the LLM')
@then(u'the schema is minified by removing spaces and non-essential metadata before sending')
def step_impl(context):
    raise StepNotImplementedError(u'Then the schema is minified by removing spaces and non-essential metadata before sending')
