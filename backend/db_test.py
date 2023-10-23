import json
from database.suggested_courses import courses_suggestion
from database import course_dependency
from database import available_course
from database import validate_course_name
from database import course_search

# print(json.dumps({'name': 'computer networks I',
#                   'code': 325, 'workload': 'high',
#                   'level': 'high', 'concentration': False, 'breath': False,
#                            'core': False, 'dislike': False}))
# result = json.loads(
#     "{\"name\": \"Logic Design and Computer Organization\", \"code\": 281, \"workload\": null, \"level\": \"high\", \"concentration\": false, \"breath\": false, \"core\": false, \"dislike\": \"true\"}")
# print(result)

result = courses_suggestion(). \
    suggested_courses('sophomore', 'CS', 'databases',
                      [26, 66],
                      []
                      )

for course in result:
    print(course['name'] + ' ' + str(course['priority']))

# result = courses_suggestion(). \
#     suggested_courses('sophomore', 'CS', 'databases',
#                       ["Introduction to Programming in Java",
#                        "Introduction to Data Structures",
#                        "Introduction to Data Science and Engineering for Majors",
#                        "Calculus for Science and Engineering I",
#                        "Principles of Chemistry for Engineers"],
#                       [{"name": "Logic Design and Computer Organization", "code": 281, "workload": 'ok',
#                           "level": "ok", "concentration": False, "breath": False, "core": False, "dislike": True},
#                        {"name": "General Physics I - Mechanics", "code": 121, "workload": 'ok', "level": 'ok', "concentration": False, "breath": False, "core": False, "dislike": True}]
#                       )

# for course in result:
#     print(course['name'] + ' ' + str(course['priority']))

# result = course_dependency(75)
# print(result)

# result = available_course(
#     [66, 26, 93, 107, 114], True, 'sophomore')
# print(result)
# for course in result:
#     print(course['name'] + " ")

# result = validate_course_name('introduction to programming in jva')
# result = [course['name'] for course in result]
# print(result)

# result = course_search(
#     {'name': 'introduction to programming in jva', 'credits': None, 'code_low': 100, 'code_high': 500, 'department': None})
# for course in result:
#     print(course["name"] + ' ' + str(course['code']))

# print(json.dumps([26, 66]))
# print(json.loads("[26, 66]"))
