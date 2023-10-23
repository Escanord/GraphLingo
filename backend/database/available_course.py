from neo4j import GraphDatabase
from .course_search import course_search
from .course_dependency import course_dependency


class available_courses:
    def __init__(self):
        uri = "neo4j+s://a44eed99.databases.neo4j.io"
        user = "neo4j"
        password = "c6Yck69jGtBHCbNKxfRJ9pzX-LZrAKzuZabPo_98z4s"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    # close the driver after using
    def close(self):
        self.driver.close()

    @staticmethod
    def possible_courses(tx, ids, exclude_taken_courses):
        courses = []
        for id in ids:
            query = "match (prereq : Course) where not (prereq)-[:REQUIRE]->() return distinct prereq union match (course : Course)-[:PREREQUISITE_OF*..1]->(prereq : Course) where course.courseID = " + str(id) + \
                " return distinct prereq;"

            avails = tx.run(query)
            avails = [course.data()['prereq'] for course in avails]
            for course in avails:
                if (course not in courses):
                    if (not exclude_taken_courses):
                        courses.append(course)
                    elif (course['courseID'] not in ids):
                        courses.append(course)
        return courses

    @staticmethod
    def filter_standing(courses, standing):
        if (standing == 'junior' or standing == 'senior'):
            return courses
        for course in courses:
            if (course['studentStandingPrerequisite'] == 'junior & senior'):
                courses.remove(course)

        return courses

    @staticmethod
    def available_courses(tx, ids, exclude_taken_courses, standing):
        result = []
        all_courses = available_courses.possible_courses(
            tx, ids, exclude_taken_courses)
        for course in all_courses:
            query = "match (course : Course {courseID : " + str(course['courseID']) + \
                "})-[:REQUIRE *0..]->(prereq : Course) return distinct prereq;"
            courses = tx.run(query)
            dependencies = [course.data()['prereq'] for course in courses]

            isIn = True
            if (dependencies):
                for dependency in dependencies:
                    if (dependency['courseID'] not in ids and dependency['courseID'] != course['courseID']):
                        isIn = False
                        break
                if(isIn):
                    result.append(course)

        return available_courses.filter_standing(result, standing)

    def available_course(self, ids, exclude_taken_courses, standing):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.available_courses, ids, exclude_taken_courses, standing
            )
            self.close()
            return result
