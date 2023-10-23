import json
import cmn_utilities as ut
import api_gateway as api

def handle(intent_request):
    # What are the saved values?
    slots = intent_request['currentIntent']['slots']
    
    # Grab all variable information:
    # course_name = ut.try_ex(lambda: slots['course_name'])
    # logger.debug(intent_request)
    taken_courses = intent_request['inputTranscript']

    # logger.debug(intent_request['inputTrasncript'])
    # Set the session:
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    if intent_request['invocationSource'] == 'DialogCodeHook':
        if('init' not in session_attributes):
            session_attributes["init"] = "false"
            return ut.elicit_slot(
                    session_attributes,
                    intent_request['currentIntent']['name'],
                    slots,
                    "taken_courses",
                    {'contentType': 'PlainText', 'content': ut.form_response("Please enter a comma deliminated list of your courses.")})
        
            # Load history and track the current search.
        # session_attributes['current_search'] = json.dumps({
        #     'taken_courses': taken_courses,
        #     'init': "false"
        # })
        
        slots['taken_courses'] = taken_courses
    
        # DialogCodeHook is intermediate hooks for validation:
        # 
        #     # Filter out searching requests
        return ut.delegate(session_attributes, slots)

    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        
        # result = json.dumps(api.available_course({'taken_courses': ut.parse_course_list(taken_courses)}))
        
        searcher = api.available_courses()
        print(searcher)
        print(ut.parse_course_list(taken_courses))
        courses = searcher.available_course(ut.parse_course_list(taken_courses))[:10]
        print(courses)
        results = json.dumps(courses)
        print(results)
        # session_attributes['testing'] = results
        
        # SEARCH COMPLETE, run second lambda, return results.
        # results = json.dumps(api.course_search({
        #     'name': course_name, 
        #     'credits': course_credits, 
        #     'code_low':course_code_low,
        #     'code_high':course_code_high, 
        #     'department':course_department
        # }))
        
        # courses_ed = {
        #     'type': "course_list",
        #     'from_s3': False,
        #     'data': courses
        # }
        
        # courses_ed = ut.form_expansion_data("course_list", False, courses)
        result = ut.form_response("Your results are as follows.", "list", None, [
            ut.form_expansion_data("course_list", False, courses)
        ])
        
        return ut.close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': result
            }
        )
        
        return ut.close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': f"The possible courses after {taken_courses} are as follows: {result}"
            })

    # Logical error, should not reach. Close.
    return ut.close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Some logical error has occured, closing instance' + taken_courses
        }
    )