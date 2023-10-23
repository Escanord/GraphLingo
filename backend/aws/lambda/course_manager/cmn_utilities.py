#Utilities common for LEX response generation and logic
import re
import json

def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response
    
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def request_slot(slots):
    # course_code = try_ex(lambda: slots['course_code'])
    # course_name = try_ex(lambda: slots['course_name'])
    # course_department = try_ex(lambda: slots['course_department'])
    # course_credits = try_ex(lambda: slots['course_credits'])
    course_search_method = try_ex(lambda: slots['course_search_method'])
    
    return build_validation_result(
        False,
        course_search_method,
        "Please enter the value."
    )

def elicit_search_method(
        session_attributes, 
        intent_name, 
        slots, 
        course_search_method,
        message
    ):
    slots['course_search_method'] = None
    session_attributes['method_added']="true"
    return elicit_slot(
        session_attributes,
        intent_name,
        slots,
        course_search_method,
        {'contentType': 'PlainText', 'content': message}
    )
    
def parse_course_list(course_string):
    return re.split(' *,+ *', course_string)
    
'''
If we constructed an s3 object as data is too large, pass data as an s3 link.
'''
def form_expansion_data(type, from_s3, data):
    return {
        'type': type,
        'from_s3': from_s3,
        'data': data
    }
    
    
# ========== NEW INTENT FULLFILLMENT: ==========

# Create a lex response
def form_response(message, type="msg", data=[], expansionData=[], stringify=False):
    response_object = {
        'type': type,
        'message': message,
        'data': data,
        'expansionData': expansionData
    }
    
    return response_object if not stringify else json.dumps(response_object)

# CREATES THE DATA OBJECT PROVIDED IN RESPONSES
def form_response_data(type, from_s3, data):
    return {
        'type': type,
        'from_s3': from_s3,
        'data': data
    }

# Elicit a slot
def lex_ellicit(
    session_attributes,
    intent,
    slots,
    slot_to_elicit,
    message,
    stringify = True
):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': {
                'contentType': 'PlainText',
                'content': message if not stringify else json.dumps(message)
            }
        }
    }

# Fullfill the lex repsonses
def lex_fullfill(
    session_attributes,
    payload,
    stringify = True
):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': "Fulfilled",
            'message': {
                'contentType': 'PlainText',
                'content': payload if not stringify else json.dumps(payload) 
                
            }
        }
    }