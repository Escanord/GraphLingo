from neo4j import GraphDatabase
# from course_search import course_search
# from course_dependency import course_dependency


# from neo4j import GraphDatabase


class course_search:

    hasPredicate = False

    def __init__(self):
        uri = "neo4j+s://a44eed99.databases.neo4j.io"
        user = "neo4j"
        password = "c6Yck69jGtBHCbNKxfRJ9pzX-LZrAKzuZabPo_98z4s"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    # close the driver after using
    def close(self):
        self.driver.close()

    @staticmethod
    def name_predicate(name):
        course_search.hasPredicate = True
        return "WHERE n.name = '" + name + "' "

    @staticmethod
    def credit_predicate(credit):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE n.credit = " + str(credit) + " "
        else:
            return "AND n.credit = " + str(credit) + " "

    @staticmethod
    def lowCode_predicate(lowCode):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE n.code >= " + str(lowCode) + " "
        else:
            return "AND n.code >= " + str(lowCode) + " "

    @staticmethod
    def highCode_predicate(highCode):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE n.code <= " + str(highCode) + " "
        else:
            return "AND n.code <= " + str(highCode) + " "

    @staticmethod
    def dept_predicate(dept):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE n.departmentID = '" + dept + "' "
        else:
            return "AND n.departmentID = '" + dept + "' "

    @staticmethod
    def new_course(course):
        return {"courseID": course["courseID"]}

    @staticmethod
    def search_courses(tx, attributes):
        query = "MATCH (n : Course) "
        # adds name predicate if there is any
        query += course_search.name_predicate(
            attributes['name']) if attributes['name'] != None else ""
        # adds credit predicate if there is any
        query += course_search.credit_predicate(
            attributes['credits']) if attributes['credits'] != None else ""
        # add lower bound of courses' code if there is any
        query += course_search.lowCode_predicate(
            attributes['code_low']) if attributes['code_low'] != None else ""
        # add upper bound of courses' code if there is any
        query += course_search.highCode_predicate(
            attributes['code_high']) if attributes['code_high'] != None else ""
        # add department predicate if there is any
        query += course_search.dept_predicate(
            attributes['department']) if attributes['department'] != None else ""

        query += "RETURN n;"

        result = tx.run(query)
        return [course.data()['n'] for course in result]

    def course_search(self, attributes):
        course_search.hasPredicate = False
        with self.driver.session() as session:
            result = session.read_transaction(
                self.search_courses, attributes
            )
            self.close()
            return result



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
    def possible_courses(tx, names):
        courses = []
        for name in names:
            query = "match (course : Course {name : '" + name + \
                "'})-[:PREREQUISITE_OF]->(prereq : Course) return prereq;"

            avails = tx.run(query)
            avails = [course.data()['prereq'] for course in avails]
            for course in avails:
                if (course not in courses):
                    courses.append(course)
        return courses

    @staticmethod
    def available_courses(tx, names):
        result = []
        all_courses = available_courses.possible_courses(tx, names)
        for course in all_courses:
            query = "match (course : Course {name : '" + course['name'] + \
                "'})-[:REQUIRE *0..]->(prereq : Course) return distinct prereq;"
            courses = tx.run(query)
            dependencies = [course.data()['prereq'] for course in courses]

            isIn = True
            if (dependencies):
                for dependency in dependencies:
                    if (dependency["name"] not in names and dependency['name'] != course['name']):
                        if (course['name'] == 'Introduction to Data Structures'):
                            print(dependencies)
                            return
                        isIn = False
                        break
                if(isIn):
                    result.append(course)

        return result

    def available_course(self, names):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.available_courses, names
            )
            self.close()
            return result

# from neo4j import GraphDatabase


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
    def dependencies(tx, name):
        query = "match (course : Course {name : '" + name + \
            "'})-[:REQUIRE *0..]->(prereq : Course) return distinct prereq;"
        courses = tx.run(query)
        courses = [course.data()['prereq'] for course in courses]
        edges = []

        for course1 in courses:
            query = "match (course : Course {name : '" + course1['name'] + \
                "'})-[:REQUIRE]->(prereq : Course) return distinct prereq;"
            prereqs = tx.run(query).data()
            prereqs = [prereq['prereq'] for prereq in prereqs]
            prereqs_names = [prereq['name'] for prereq in prereqs]
            for course2 in courses:
                if (course2['name'] in prereqs_names and course1['name'] != course2['name']):
                    edges.append(
                        (course1['courseID'], course2['courseID']))

        return {'all_courses': courses, 'edges': edges}

    def course_dependency(self, name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.dependencies, name
            )
            self.close()
            return result
