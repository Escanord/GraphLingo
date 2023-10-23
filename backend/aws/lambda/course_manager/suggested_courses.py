import json
import cmn_utilities as ut
import sample_gateway as api

def handle(intent_request):
    # What are the saved values?
    slots = intent_request['currentIntent']['slots']
    
    # Grab all variable information:
    student_standing = ut.try_ex(lambda: slots['student_standing'])
    student_major = ut.try_ex(lambda: slots['student_major'])
    student_concentration = ut.try_ex(lambda: slots['student_concentration'])
    taken_courses = ut.try_ex(lambda: slots['taken_courses'])

    # Set the session:
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
        # Load history and track the current search.
    session_attributes['current_search'] = json.dumps({
        'student_standing': student_standing,
        'student_major': student_major,
        'student_concentration': student_concentration
    })
    
        
    # DialogCodeHook is intermediate hooks for validation:
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Filter out searching requests
        if(student_standing is None or
            student_major is None or
            student_concentration is None):
            return ut.delegate(
                session_attributes,
                slots)
                
        # AND THEN GET THE LIST OF COURSES LAST
        if(taken_courses is None):
            if('course_list_incoming' in session_attributes):
                taken_courses = intent_request['inputTranscript']
                slots['taken_courses'] = taken_courses
                session_attributes = {}
            else:
                session_attributes['course_list_incoming'] = "true"
            
            return ut.delegate(
                session_attributes,
                slots)
                
    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        result = json.dumps(api.suggested_courses({
            'major': student_major,
            'concentration': student_concentration,
            'standing': student_standing,
            'taken_courses': ut.parse_course_list(taken_courses)
        }))
        
        return ut.close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': f"Beginning course suggestion algorithm... results are:{result}"
            })
    
    # Logical error, should not reach. Close.
    return ut.close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Some logical error has occured, closing instance'
        }
    )