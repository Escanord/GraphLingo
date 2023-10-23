import json
import cmn_utilities as ut
import api_gateway as api
from session_manager import SessionManager

def handle(intent_request):
    # What are the slot values?
    slots = intent_request['currentIntent']['slots']
    course_name = ut.try_ex(lambda: slots['course_name'])
    
    # Grab all variable information:
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    sm = SessionManager(session_attributes)
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # FIRST STEP
        if(sm.checkStepAndIncrement(0)):
            return ut.lex_ellicit(
                    sm.patchAttributes(session_attributes),
                    intent_request['currentIntent']['name'],
                    slots,
                    "course_name",
                    ut.form_response("What is the course's name?", stringify = False)
                )
                
        # Else, course name passed:
        slots['course_name'] = intent_request['inputTranscript']
        
        return ut.delegate(session_attributes, slots)

    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        searcher = api.course_dependency()
        dependencies = searcher.course_dependency(course_name)

        # Form the expansion data of graphs:
        nodes = [{'key': course['courseID'], 'name': course['name']} for course in dependencies['all_courses']]
        links = [{'from': edge[0], 'to':edge[1]} for edge in dependencies['edges']]
        
        expansions = [
            ut.form_expansion_data("course_list", False, dependencies['all_courses']),      # For creating a course list
            ut.form_expansion_data("dep_graph", False, {'nodes': nodes, 'links': links})    # For creating a graph
        ]
        
        response = ut.form_response("The dependencies are as follows.", "list", [], expansions)
        
        return ut.lex_fullfill(
            session_attributes,
            response)

    # Logical error, should not reach. Close.
    return ut.close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Some logical error has occured, closing instance' + course_name
        }
    )