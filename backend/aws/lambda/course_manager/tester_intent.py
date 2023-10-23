import json                 # Allows for working with json
import cmn_utilities as ut  # Simple message construction

'''
ORDER OF EVENTS:
1. Will try and see what to do, sees that sample_value_two is not set.
    - We tell lex to try and get sample_value_two first.
2. After being set, we validate, and see that sample two is set.
    - Since it is set, we go and deligate our functionality for LEX to decide.
    - Lex sees that there is a required value for sample_value_one so decides to ask for that value.
3. After that value is set, since value two is still set, we delegate again.
    - Lex sees that all its requirements are finished (sample_value_one) and moves to fullfilment:
4. On fullfilment, we can construct our dictionary and pass the resulting message.

'''


def handle(intent_request):
    # What are the saved values from the intent that are being updated?
    slots = intent_request['currentIntent']['slots']
    
    # Grab all variable information from the slots (Get key, if not set, return None):
    sample_value_one = ut.try_ex(lambda: slots['sample_value_one'])
    sample_value_two = ut.try_ex(lambda: slots['sample_value_two'])

    # Initiailize the session attributes, will be empty object if not present:
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    # Pass previous values into the session attributes.
    session_attributes['from_slots'] = json.dumps({
        'sample_value_one': sample_value_one,
        'sample_value_two': sample_value_two
    })
    
    # Send fullfilment response:
    results = ut.form_response(
            "This is the message",
            "url",
            [
                ut.form_expansion_data('url', True, 'https://cwru-chatbot.s3.amazonaws.com/sample.json'),
                ut.form_expansion_data('random', True, 'https://cwru-chatbot.s3.amazonaws.com/sample.json')
            ],
            [
                ut.form_expansion_data('ex1', True, 'https://cwru-chatbot.s3.amazonaws.com/sample.json'),
                ut.form_expansion_data('ex2', True, 'https://cwru-chatbot.s3.amazonaws.com/sample.json')
            ]
            
        )
    
    return ut.close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': results
            })
    
    # INTERMEDIATE RESPONSE VALIDATION (Between each response)
    if intent_request['invocationSource'] == 'DialogCodeHook':
        
        # DO WE HAVE VALUE 2?
        if(sample_value_two is None):
            # No, FORCE Lex to look for value 2
            return ut.elicit_slot(
                    session_attributes,
                    intent_request['currentIntent']['name'],
                    slots,
                    "sample_value_two",
                    {'contentType': 'PlainText', 'content': ut.form_response("Please enter the value for value 2:")})

        # OTHERWISE, let lex decide what to do. 
        return ut.delegate(
            session_attributes, 
            slots
        )

    # FINAL FULLFILMENT
    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        
        # If you give me all responses, they are easily randomoized on the front end.
        # result_structure = {
        #     'type': "random",
        #     'data': [
        #         f"response1From({sample_value_one})",
        #         f"response2From({sample_value_two})"
        #     ]
        # }
        
        
        return ut.close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': json.dumps(result_structure)
            })

    # LOGICAL ERROR, should not reach. Close.
    return ut.close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Some logical error has occured, closing instance.'
        }
    )