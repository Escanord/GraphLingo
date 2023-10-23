import requests
import os
from ast import literal_eval
from dotenv import load_dotenv
from utils.crawler import get_main_text
from utils.prompts import course_entities_extraction_prompt, course_outcome_extraction_prompt, course_goal_extraction_prompt, question_entities_extraction_prompt
from neo4j import GraphDatabase

load_dotenv()
GPTKey = os.getenv('GPTKey')
driver = None


def connect_dbms():
    uri = os.getenv('URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    global driver
    driver = GraphDatabase.driver(uri, auth=(user, password))


def close():
    driver.close()


def extract_entities(URL):
    raw_text = get_main_text(URL)
    text = []

    for child in raw_text:
        text.append(child.prettify())

    entities = extract_entities(text)

    inject_entities(entities)


def create_entities(tx, pair):
    tx.run("""MERGE (entity1:Node {name: $entity1})
           MERGE (entity1)-[:relation{name: $rel}]->(entity2:Node {name: $entity2})""",
           entity1=pair[0], rel=pair[1], entity2=pair[2])


def inject_entities(entities):
    connect_dbms()
    with driver.session() as session:
        for pair in entities:
            session.execute_write(create_entities, pair)
    close()


class course_builder:
    def __init__(self, lines):
        self.lines = lines
        self.section_flag = 0
        self.course_name = ''
        self.course_code = ''
        self.topics = []
        self.outcomes = []
        self.textbook = []
        self.description = []
        self.goals = []
        self.instructor = ''
        self.credit_hour = 0
        self.contact_hour = 0

    def update_data(self, lines):
        self.lines = lines

    def __update_section_flag(self, line):
        if 'Instructor' in line:
            self.section_flag = 1
        elif 'Contact Hours' in line:
            self.section_flag = 2
        elif 'Credit Hours' in line:
            self.section_flag = 3
        elif 'Textbook' in line:
            self.section_flag = 4
        elif 'Supplemental Material' in line:
            self.section_flag = 4
        elif 'Description' in line:
            self.section_flag = 5
        elif 'Prerequisite' in line:
            self.section_flag = 6
        elif 'Course Role in Data Science Major' in line:
            self.section_flag = 7
        elif 'Course Goal' in line:
            self.section_flag = 8
        elif 'Course Outcomes' in line:
            self.section_flag = 9
        elif 'Course Topics' in line:
            self.section_flag = 10

        if ':' in line:
            line = line.split(':')[1]

        return line

    def retrieve_entities(self):
        for line in self.lines:
            line = self.__update_section_flag(line)
            if self.section_flag == 0:
                try:
                    self.course_code, self.course_name = line.split('–')
                except:
                    self.course_code, self.course_name = line.split('-')
            elif self.section_flag == 1:
                self.instructor = line
            elif self.section_flag == 2:
                self.contact_hour = line
            elif self.section_flag == 3:
                self.credit_hour = line
            elif self.section_flag == 4:
                self.textbook.append(line)
            elif self.section_flag == 5:
                self.description.append(line)
            elif self.section_flag == 8:
                self.goals.append(line)
            elif self.section_flag == 9:
                self.outcomes.append(line)
            elif self.section_flag == 10:
                self.topics.append(line)

    def inject_course_info(self):
        def extract_entities(text, prompt):
            request_body = {
                "model": "text-davinci-003",
                "temperature": 0.3,
                "max_tokens": 800,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "prompt": prompt + '\n'.join(text),
            }

            request_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GPTKey}',
            }

            response = requests.post('https://api.openai.com/v1/completions',
                                     json=request_body, headers=request_headers, timeout=60)

            entities = response.json()
            # returned valued from GPT is in form '\n[...]' so remove the first character
            entities = entities['choices'][0]['text'].split(':')[1][1:]
            entities = literal_eval(entities)

            return entities

        def create_course(tx, name, code, credit):
            tx.run("""
                    MERGE (course: Course{name: $course_name})
                    SET course.code = $course_code, course.credit = $course_credit""",
                   course_name=name, course_code=code, course_credit=credit)

        def inject_instructor(tx, name, instructor):
            tx.run("""
                   MERGE (prof: Professor{name: $course_instructor})
                   """,
                   course_instructor=instructor)
            tx.run("""
                   MATCH (course: Course{name: $course_name})
                   MATCH (prof: Professor{name: $course_instructor})
                   MERGE (course)-[:taughtBy]-(prof)
                   """,
                   course_name=name, course_instructor=instructor)

        def inject_topics(tx, name, topics):
            entities = extract_entities(
                topics, course_entities_extraction_prompt)

            for topic in entities:
                tx.run("""
                    MATCH (course: Course{name: $course_name})
                    MERGE (topic: Topic{name: $course_topic})
                    MERGE (course)-[:hasTopic]-(topic)
                    """,
                       course_name=name, course_topic=topic)

        def inject_outcomes(tx, name, outcomes):
            entities = extract_entities(
                outcomes, course_outcome_extraction_prompt)

            for outcome in entities:
                tx.run("""
                    MATCH (course: Course{name: $course_name})
                    MERGE (outcome: CourseOutcome{name: $course_outcome})
                    MERGE (course)-[:hasOutcome]-(outcome)
                    """,
                       course_name=name, course_outcome=outcome)

        def inject_textbook(tx, name, textbooks):
            entities = textbooks[:len(textbooks) - 1]

            for textbook in entities:
                tx.run("""
                    MATCH (course: Course{name: $course_name})
                    MERGE (textbook: TextBook{name: $course_textbook})
                    MERGE (course)-[:hasTextbook]-(textbook)
                    """,
                       course_name=name, course_textbook=textbook)

        def inject_goals(tx, name, goals):
            entities = extract_entities(goals, course_goal_extraction_prompt)

            for goal in entities:
                tx.run("""
                    MATCH (course: Course{name: $course_name})
                    MERGE (goal: CourseGoal{name: $course_goal})
                    MERGE (course)-[:hasGoal]-(goal)
                    """,
                       course_name=name, course_goal=goal)

        def inject_description(tx, name, description):
            entities = extract_entities(
                description, course_entities_extraction_prompt)

            full_description = ' '.join(description)

            tx.run("""
                    MATCH (course: Course{name: $course_name})
                    MERGE (description: CourseDescription{course_name: $course_name, description: $course_description})
                    MERGE (course)-[:isDescribed]-(description)
                    """,
                   course_name=name, course_description=full_description)

            for desc in entities:
                tx.run("""
                    MATCH (course: Course{name: $course_name})-[:isDescribed]-(description)
                    MERGE (desc: Node{name: $course_description})
                    MERGE (description)-[:has]-(desc)
                    """,
                       course_name=name, course_description=desc)

        # ---- # ---- #
        connect_dbms()
        with driver.session() as session:
            session.execute_write(
                create_course, self.course_name, self.course_code, self.credit_hour
            )
            session.execute_write(
                inject_instructor, self.course_name, self.instructor
            )
            session.execute_write(
                inject_topics, self.course_name, self.topics
            )
            session.execute_write(
                inject_outcomes, self.course_name, self.outcomes
            )
            session.execute_write(
                inject_textbook, self.course_name, self.textbook
            )
            session.execute_write(
                inject_goals, self.course_name, self.goals
            )
            session.execute_write(
                inject_description, self.course_name, self.description
            )
        close()

    def print_all(self):
        print(self.section_flag)
        print(self.course_name)
        print(self.course_code)
        print(self.topics)
        print(self.outcomes)
        print(self.textbook)
        print(self.description)
        print(self.goals)
        print(self.instructor)
        print(self.credit_hour)
        print(self.contact_hour)


# URL = 'https://bulletin.case.edu/engineering/computer-data-sciences/data-science-analytics-bs/'
# extract_entities(URL)
