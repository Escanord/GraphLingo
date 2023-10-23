from .available_course import available_courses
from .course_search import course_search
from .course_dependency import course_dependency

if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    uri = "neo4j+s://a44eed99.databases.neo4j.io"
    user = "neo4j"
    password = "c6Yck69jGtBHCbNKxfRJ9pzX-LZrAKzuZabPo_98z4s"

    # search = course_search()
    # result = search.course_search(
    #     {'name': 'introduction to programming in java', 'credits': 3, 'code_low': 100, 'code_high': 199, 'department': None})
    # for course in result:
    #     print(course["name"])
    # search.close()

    # dep = course_dependency()
    # result = dep.course_dependency('advanced algorithms', 477)
    # print(result)

    # avail = available_courses()
    # result = avail.available_course(
    #     ["introduction to programming in java", "introduction to data structures"], True, 'sophomore')
    # print(result)
    # for course in result:
    #     print(course['name'])

    # duplicateChecker = course_dependency().isDuplicate('High Performance Computing')
    # print(duplicateChecker)

    # search = course_search()
    # result = search.validate_course_name('Software enGinEEriNg')
    # result = [course['name'] for course in result]
    # print(result)
