from .course_search import course_search as search
from .course_dependency import course_dependency as dependency
from .available_course import available_courses
from .suggested_courses import courses_suggestion


def validate_course_name(name):
    return search().validate_course_name(name)


def course_search(attributes):
    return search().course_search(attributes)


def course_dependency(id):
    return dependency().course_dependency(id)


def isDuplicate(name):
    return dependency().isDuplicate(name)


def available_course(ids, exclude_taken_courses, standing):
    return available_courses().available_course(ids, exclude_taken_courses, standing)


def suggested_courses(standing, major, concentration, taken_courses):
    return courses_suggestion().suggested_courses(standing, major, concentration, taken_courses)


def search_by_id(id):
    return search().search_by_id(id)
