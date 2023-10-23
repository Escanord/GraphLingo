import json
import cmn_utilities as ut
import api_gateway as api
"""
Manages course search
Beyond fulfillment, the implementation for this intent demonstrates the following:
1) Use of elicitSlot in slot validation and re-prompting
2) Use of sessionAttributes to pass information that can be used to guide conversation
"""
def handle(intent_request):
    # What are the saved values?
    slots = intent_request['currentIntent']['slots']
    
    # Grab all variable information:
    course_code_low = ut.try_ex(lambda: slots['course_search_code_low'])
    course_code_high = ut.try_ex(lambda: slots['course_search_code_high'])
    course_name = ut.try_ex(lambda: slots['course_search_name'])
    course_department = ut.try_ex(lambda: slots['course_search_department'])
    course_credits = ut.try_ex(lambda: slots['course_search_credits'])
    course_search_method = ut.try_ex(lambda: slots['course_search_method'])
    add_parameter = ut.try_ex(lambda: slots['add_parameter'])

    # Set the session:
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {'method_added':"false"}
    
        # Load history and track the current search.
    session_attributes['current_search'] = json.dumps({
        'course_search_code_low': course_code_low,
        'course_search_code_high': course_code_high,
        'course_search_name': course_name,
        'course_search_department': course_department,
        'course_search_credits': course_credits,
        'course_search_method': course_search_method,
        'add_parameter' : add_parameter
    })
    
        # Track if at least one method has been added.
    if (not 'method_added' in session_attributes):
        session_attributes['method_added']="false"
        
    # DialogCodeHook is intermediate hooks for validation:
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Filter out searching requests
        if(course_search_method is not None):
            return ut.elicit_search_method(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                course_search_method,
                ut.form_response("Please enter the search value:")
                )
        
        # We have not added a search method
        if(session_attributes['method_added'] == "false"):
            # return delegate(session_attributes, slots)
            return ut.elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                "course_search_method",
                {'contentType': 'PlainText', 'content': ut.form_response("How would you like to search for a course?")}
            )
        elif(add_parameter == "true"):
            slots['add_parameter'] = None
            # return delegate(session_attributes, slots)
            return ut.elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                "course_search_method",
                {'contentType': 'PlainText', 'content': ut.form_response("How would you like to search for a course?")}
            )
        # We have added a search method, ask if we want another
        elif(add_parameter == None):
            return ut.elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                "add_parameter",
                {'contentType': 'PlainText', 'content': ut.form_response("Would you like to add a parameter to your search? (y/n)")}
            )
        else:
            query = {
                'name': course_name, 
                'credits': course_credits, 
                'code_low':course_code_low,
                'code_high':course_code_high, 
                'department':course_department
            }
            searcher = api.course_search()
            print(searcher)
            courses = searcher.course_search(query)[:10]
            print(courses)
            results = json.dumps(courses)
            print(results)
            session_attributes['testing'] = results
            
            # SEARCH COMPLETE, run second lambda, return results.
            # results = json.dumps(api.course_search({
            #     'name': course_name, 
            #     'credits': course_credits, 
            #     'code_low':course_code_low,
            #     'code_high':course_code_high, 
            #     'department':course_department
            # }))
            
            courses_ed = {
                'type': "course_list",
                'from_s3': False,
                'data': courses
            }
            
            courses_ed = ut.form_expansion_data("course_list", False, courses)
            
            result = ut.form_response("Your results are as follows.", "list", None, [courses_ed])
            
            return ut.close(
                session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': result
                }
            )

    # Logical error, should not reach. Close.
    return ut.close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Some logical error has occured, closing instance'
        }
    )