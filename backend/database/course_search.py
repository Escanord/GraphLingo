from neo4j import GraphDatabase


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
    def fuzzy_predicate(name):
        return 'CALL db.index.fulltext.queryNodes("courses_name", "' + \
            name + '~") YIELD node, score match (node : Course) '

    @staticmethod
    def name_predicate(name):
        course_search.hasPredicate = True
        return "WHERE node.name =~ '(?i)" + name + "' "

    @staticmethod
    def credit_predicate(credit):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE node.credit = " + str(credit) + " "
        else:
            return "AND node.credit = " + str(credit) + " "

    @staticmethod
    def lowCode_predicate(lowCode):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE node.code >= " + str(lowCode) + " "
        else:
            return "AND node.code >= " + str(lowCode) + " "

    @staticmethod
    def highCode_predicate(highCode):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE node.code <= " + str(highCode) + " "
        else:
            return "AND node.code <= " + str(highCode) + " "

    @staticmethod
    def dept_predicate(dept):
        if (not course_search.hasPredicate):
            course_search.hasPredicate = True
            return "WHERE node.departmentID =~ '(?i)" + dept + "' "
        else:
            return "AND node.departmentID = '" + dept + "' "

    @staticmethod
    def new_course(course):
        return {"courseID": course["courseID"]}

    @staticmethod
    def build_query(query, attributes):
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

        query += "RETURN node order by node.departmentID, node.code;"
        return query

    @staticmethod
    def search_courses(tx, attributes):
        # adds name predicate if there is any
        query = course_search.fuzzy_predicate(
            attributes['name']) if attributes['name'] != None else "MATCH (node : Course) "
        query = course_search.build_query(query, attributes)
        result = tx.run(query)
        result = [course.data()['node'] for course in result]

        exact_query = "MATCH (node : Course) "
        course_search.hasPredicate = False
        exact_query += course_search.name_predicate(
            attributes['name']) if attributes['name'] != None else ""
        exact_query = course_search.build_query(exact_query, attributes)
        exact_result = tx.run(exact_query)
        exact_result = [course.data()['node'] for course in exact_result]
        if (len(exact_result) > 0):
            result = exact_result

        return result

    def course_search(self, attributes):
        course_search.hasPredicate = False
        with self.driver.session() as session:
            result = session.read_transaction(
                self.search_courses, attributes
            )
            self.close()
            return result

    @staticmethod
    def correct_course_name(tx, name):
        query = "MATCH (n : Course) WHERE n.name =~ '(?i)" + \
            name + "' return n;"
        result = tx.run(query)
        courses = [course.data()['n'] for course in result]
        if (len(courses) > 0):
            return courses
        query = 'CALL db.index.fulltext.queryNodes("courses_name", "' + \
            name + '~") YIELD node, score return node;'
        result = tx.run(query)
        return [course.data()['node'] for course in result]

    def validate_course_name(self, name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.correct_course_name, name
            )
        self.close()
        return result

    @staticmethod
    def course_name_of(tx, id):
        query = "MATCH (n : Course) WHERE n.courseID = " + \
            str(id) + " return n;"
        result = tx.run(query)
        return [course.data()['n'] for course in result]

    def search_by_id(self, id):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.course_name_of, id
            )
        self.close()
        return result
