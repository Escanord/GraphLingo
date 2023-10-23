from neo4j import GraphDatabase


class course_dependency:

    def __init__(self):
        uri = "neo4j+s://a44eed99.databases.neo4j.io"
        user = "neo4j"
        password = "c6Yck69jGtBHCbNKxfRJ9pzX-LZrAKzuZabPo_98z4s"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    # close the driver after using
    def close(self):
        self.driver.close()

    @staticmethod
    def dependencies(tx, id):
        query = "match (course : Course)-[:REQUIRE *0..]->(prereq : Course) where course.courseID = " + str(id) + \
            " return distinct prereq;"
        courses = tx.run(query)
        courses = [course.data()['prereq'] for course in courses]
        edges = []

        for course1 in courses:
            query = "match (course : Course {courseID : " + str(course1['courseID']) + \
                "})-[:REQUIRE]->(prereq : Course) return distinct prereq;"
            prereqs = tx.run(query).data()
            prereqs = [prereq['prereq'] for prereq in prereqs]
            prereqs_ids = [prereq['courseID'] for prereq in prereqs]
            for course2 in courses:
                if (course2['courseID'] in prereqs_ids and course1['courseID'] != course2['courseID']):
                    edges.append(
                        (course1['courseID'], course2['courseID']))

        return {'all_courses': courses, 'edges': edges}

    def course_dependency(self, id):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.dependencies, id
            )
            self.close()
            return result

    @staticmethod
    def checkDuplicate(tx, name):
        query = "match (n : Course) where n.name =~ '(?i)" + \
            name + "' return distinct n;"
        courses = tx.run(query)
        courses = [course.data()['n'] for course in courses]
        return len(courses) > 1

    def isDuplicate(self, name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.checkDuplicate, name
            )
            self.close()
            return result
