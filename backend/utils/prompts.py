entity_extraction_prompt = """Given a prompt in HTML format, extrapolate as many relationships as possible from it. Provide entity-relationship pair in the form of [ENTITY 1, RELATIONSHIP, ENTITY 2]. 
The relationship is directed, so the order matters. There can be multiple relationships in a single statement.  
The relationship should be appropriate to be used in knowledge graph.
Example:
prompt: Alice is Bob's roommate and they are friendly.
[["Alice", "roommate", "Bob"], ["Alice and Bob", "are", "friendly"]]

prompt:"""

course_entities_extraction_prompt = """ Given a prompt in text, extrapolate as many Computer Science-related entities from it as possible.
The entities should be appropriate to be used in knowledge graph. Output form should be in an array-form.
Example:
prompt: Abstract data types; generic types; linked lists
entities: ["Abstract data types", "generic types", "linked lists"]

prompt:
"""
question_entities_extraction_prompt = """Given a question, extrapolate as many entity-relationship triple from it. The entity that the question 
is asking for should be represented by a question mark.
Example:
question: Who is the professor of CSDS 234?
[['?','professor of', 'CSDS 234']]
question: What can I learn from CSDS 310?
[['?', 'can learn from', 'CSDS 310']]

question=
"""
course_outcome_extraction_prompt = """Given a prompt in text, extrapolate as many Computer Science-related expected outcomes from it as possible.
The outcomes should be appropriate to be used in knowledge graph. Output form should be in an array-form. Output should not have any special character at the end such as '.' or ','.
Example:
prompt: 5. Know how to design and format code so that it is easy to read and to understand.6. Know how to write documentation for an API.7. Be able to work in a paired -programming team.
entities: ["Know how to design and format code so that it is easy to read and to understand", "Know how to write documentation for an API", "Be able to work in a paired -programming team"]

prompt:
"""

course_goal_extraction_prompt = """Given a prompt in text, extrapolate as many Computer Science-related expected goals from it as possible.
The goals should be appropriate to be used in knowledge graph. Output form should be in an array-form.
Example:
prompt: 'Specific Course Goals  ', ' The primary goal of the course is to develop the ability to write algorithms in the Java programming language.  Additional goals are to understand how to break down a complex problem into simple, unambiguous steps, how to test and debug a program, and how to write a program so that it easily communicates what it does to a human reader.  '
entities: [" develop the ability to write algorithms in the Java programming language", "understand how to break down a complex problem into simple and unambiguous steps", "know how to test and debug a program", "know how to write a program so that it easily communicates what it does to a human reader"]

prompt:
"""

suggestion_example_prompt = """
For example:
Triple: [code:CSDS 132  name: Introduction to Programming in Java  credit: 3 , hasTopic, Graphical User Interfaces,]

Suggested follow-up question: Can you tell me more about the topic Graphical User Interfaces that is introduced in CSDS 132?
"""