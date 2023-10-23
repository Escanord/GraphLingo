import logging
from neo4j import GraphDatabase
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.debug("Imported neo4j")

def available_course(parameters):
    courses = []
    courses = sample_calc(parameters)
    logger.debug("Hello From available_course")
    return courses
    
def course_dependency(parameters):
    courses = {
        'all_courses': sample_calc(parameters),
        'edges': [
            {
                'course_id': 1,
                'prereq_id': 2
            }
        ]
    }
    logger.debug("Hello From course_dependency")
    return courses
    
def course_search(parameters):
    courses = []
    courses = sample_calc(parameters)
    logger.debug("Hello From course_search")
    return courses
    
def suggested_courses(parameters):
    courses = []
    courses = sample_calc(parameters)
    logger.debug("Hello From suggested_courses")
    return courses
    
def sample_calc(object):
    temp = []
    for key in object:
        temp.append(object[key])
    return temp