from os import stat
from neo4j import GraphDatabase
from .available_course import available_courses
import json


class courses_suggestion:
    def __init__(self):
        uri = "neo4j+s://a44eed99.databases.neo4j.io"
        user = "neo4j"
        password = "c6Yck69jGtBHCbNKxfRJ9pzX-LZrAKzuZabPo_98z4s"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    @staticmethod
    def concentration_prioritize(tx, courses, concentration):
        query = "match (n : Course)-[:IS_DEPTH]->(concentration : Concentration {name : '" + \
            concentration + "'}) return n;"
        depth_courses = tx.run(query)
        depth_courses = [course.data()['n'] for course in depth_courses]
        depth_ids = [course['courseID'] for course in depth_courses]
        for course in courses:
            if (course['courseID'] in depth_ids):
                course['priority'] += 1

        return courses

    @staticmethod
    def core_prioritize(courses):
        for course in courses:
            if (course['isCore']):
                course['priority'] += 2
        return courses

    @staticmethod
    def breath_prioritize(courses):
        for course in courses:
            if (course['isBreath']):
                course['priority'] += 1
        return courses

    @staticmethod
    def sages_prioritze(courses):
        for course in courses:
            if (course['name'] == 'Sages'):
                course['priority'] += 1
        return courses

    @staticmethod
    def general_engineer_prioritize(courses):
        for course in courses:
            if(course['isGeneralEngineer']):
                course['priority'] += 1
        return courses

    @staticmethod
    def unsatisfied_courses(tx, info):
        query = "MATCH (n : Course) "
        courses = []
        for course_info in info:
            course = tx.run(query + "WHERE n.courseID = " +
                            str(course_info['courseID']) + " return n;")
            course = [crs.data()['n'] for crs in course][0]
            courses.append(course)
        return courses

    @staticmethod
    def workload(unsatisfactions, unsatisfied_courses):
        result = None
        direction = None
        for uns, course in zip(unsatisfactions, unsatisfied_courses):
            if (uns['workload'] is not None):
                if (direction is None and uns['workload'] != 'ok'):
                    direction = uns['workload']
                    result = course['workload']
                elif (direction == 'high'):
                    result = min(result, course['workload'])
                elif (direction == 'low'):
                    result = max(result, course['workload'])

        return {'result': result, 'direction': direction}

    @staticmethod
    def workload_deprioritize(courses, unsatisfactions, unsatisfied_courses):
        workload = courses_suggestion.workload(
            unsatisfactions, unsatisfied_courses)
        for course in courses:
            if (workload['direction'] == 'high' and course['workload'] >= workload['result']):
                course['priority'] -= 1
            elif (workload['direction'] == 'low' and course['workload'] <= workload['result']):
                course['priority'] -= 1

        return courses

    @staticmethod
    def level(unsatisfactions, unsatisfied_courses):
        result = None
        direction = None
        for uns, course in zip(unsatisfactions, unsatisfied_courses):
            if (uns['level'] is not None):
                if (direction is None and uns['level'] != 'ok'):
                    direction = uns['level']
                    result = (course['code'] % 100) * 100
                elif (direction == 'high'):
                    result = min(result, (course['code'] % 100) * 100)
                elif (direction == 'low'):
                    result = max(result, (course['code'] % 100) * 100)

        return {'result': result, 'direction': direction}

    @staticmethod
    def level_deprioritize(courses, unsatisfactions, unsatisfied_courses):
        workload = courses_suggestion.level(
            unsatisfactions, unsatisfied_courses)
        for course in courses:
            if ('code' in course):
                if (workload['direction'] == 'high' and course['code'] >= workload['result']):
                    course['priority'] -= 1
                elif (workload['direction'] == 'low' and course['code'] <= workload['result']):
                    course['priority'] -= 1

        return courses

    @staticmethod
    def needs_requirement_priority(unsatisfactions, requirement):
        for uns in unsatisfactions:
            if (uns[requirement] == 'true'):
                return False
        return True

    @staticmethod
    def dislike_deprioritize(courses, unsatisfied_courses_codes):
        for course in courses:
            if (course['courseID'] in unsatisfied_courses_codes):
                course['priority'] -= 3
        return courses

    @staticmethod
    def suggestions(tx, standing, major, concentration, taken_courses_ids, unsatisfactions):
        courses = available_courses().available_course(taken_courses_ids, True, standing)
        for course in courses:
            course['priority'] = 0
        if (courses_suggestion.needs_requirement_priority(unsatisfactions, 'concentration')):
            courses = courses_suggestion.concentration_prioritize(
                tx, courses, concentration)
        if (courses_suggestion.needs_requirement_priority(unsatisfactions, 'core')):
            courses = courses_suggestion.core_prioritize(courses)
        if (courses_suggestion.needs_requirement_priority(unsatisfactions, 'breath')):
            courses = courses_suggestion.breath_prioritize(courses)

        courses = courses_suggestion.sages_prioritze(courses)
        courses = courses_suggestion.general_engineer_prioritize(courses)
        unsatisfied_courses = courses_suggestion.unsatisfied_courses(
            tx, [{'courseID': uns['courseID']} for uns in unsatisfactions])
        courses = courses_suggestion.workload_deprioritize(
            courses, unsatisfactions, unsatisfied_courses)
        courses = courses_suggestion.level_deprioritize(
            courses, unsatisfactions, unsatisfied_courses)

        courses = courses_suggestion.dislike_deprioritize(
            courses, [course['courseID'] for course in unsatisfactions if course['dislike'] == 'true'])
        print([course['name'] for course in courses])

        return courses

    def suggested_courses(self, standing, major, concentration, taken_courses_ids, unsatisfactions):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.suggestions, standing, major, concentration, taken_courses_ids, unsatisfactions
            )
            self.close()
            result.sort(key=lambda course: -course['priority'])
            return result[:5]


# result = courses_suggestion(). \
#     suggested_courses('sophomore', 'CS', 'software_engineering',
#                       ["introduction to programming in java",
#                           "introduction to data structures"],
#                       [{'name': 'software engineering',
#                           'code': 393, 'workload': 'high'}]
#                       )

# for course in result:
#     print(course['name'] + ' ' + str(course['priority']))
