from behave import given, when, then
from src.test_pipeline import add

@given("due numeri 2 e 3")
def step_given_numbers(context):
    context.a = 2
    context.b = 3

@when("li sommo")
def step_when_add(context):
    context.result = add(context.a, context.b)

@then("il risultato deve essere 5")
def step_then_result(context):
    assert context.result == 5
