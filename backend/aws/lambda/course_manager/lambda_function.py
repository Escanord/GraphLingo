import json
import datetime
import time
import os
import dateutil.parser
import logging
import sample_gateway
import cmn_utilities as ut
import course_dependency
import course_search
import available_courses
import suggested_courses
import tester_intent

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

"""
Called when the user specifies an intent for this bot.
"""
def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'course_search':
        return course_search.handle(intent_request)
    elif intent_name == 'available_courses':
        return available_courses.handle(intent_request)
    elif intent_name == 'course_dependency':
        return course_dependency.handle(intent_request)
    elif intent_name == 'suggested_courses':
        return suggested_courses.handle(intent_request)
    elif intent_name == 'sample_intent':
        return tester_intent.handle(intent_request)

    # Cannot find the intent
    raise Exception('Intent with name ' + intent_name + ' not supported')


"""
Route the incoming request based on intent.
The JSON body of the request is provided in the event slot.

Callend with lex
"""
def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    # logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    # Get the return from the dispatcher
    # logger.debug(event)
    # logger.debug(event['inputTranscript'])
    # logger.debug(json.dumps(context)) #To CRASH
    return dispatch(event)