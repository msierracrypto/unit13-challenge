### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        if age is not None:
            if age < 0 and age > 65:
                return build_validation_result(False, elicitSlot, "You must be between 0 and 65 years of age. Please provide your age again.")
                
        if investment_amount < 5000:
            return build_validation_result(False, elicitSlot, "The amount should be greater than 5000. Please enter the amount again.")

        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    initial_recommendation = ""
    if risk_level.lower() == 'none':
        initial_recommendation = 'Invest 100%: all $'+ investment_amount + ' in bonds(AGG), 0% equities (SPY)'
    elif risk_level.lower() == 'very low':
        initial_recommendation = 'Invest 80%: $'+ str(int(investment_amount) * 0.8) + ' in bonds(AGG) and 20%: $' + str(int(investment_amount) * 0.2) +' in equities (SPY).'
    elif risk_level.lower() == 'low':
        initial_recommendation = 'Invest 60%: $'+ str(int(investment_amount) * 0.6) + ' in bonds(AGG) and $' + str(int(investment_amount) * 0.4) +' in equities (SPY).'
    elif risk_level.lower() == 'medium':
        initial_recommendation = 'Invest 40%: $'+str(int(investment_amount)*.4) + 'in bonds(AGG) and 60%: $' + str(int(investment_amount)*.6)+' in equities (SPY).'  
    elif risk_level.lower() == 'high':
        initial_recommendation = 'Invest 20%: $'+str(int(investment_amount)*.2) + 'in bonds(AGG) and 80%: $' + str(int(investment_amount)*.8)+' in equities (SPY).'
    elif risk_level.lower() == 'very high':
        initial_recommendation = 'Invest 0% in bonds(AGG) and 100%: '+investment_amount+' in equities (SPY).'
    else:
        return build_validation_result(False, elicitSlot, "The initial_recommendation object is not equal to one of our recommendations")

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
