next_triples_prompt = """
For example: 
Cypher query:
MATCH (n:Student) - [r:TaughtBy] - (m:Professor)
WHERE m.interestField = “Database”
RETURN n
To decompose this Cypher query into a set of graph triples in the form of (subject, verb, object), possible triples are:
( n: student, taughtBy, m : professor)
(m : professor, hasInterestField, Database)
Only Give me possible next triples to decompose this query: 
"""

remove_triple_prompt = """
Example 1: 
Graph query:
MATCH (n:Student) - [r:TaughtBy] - (m:Professor)
WHERE m.interestField = “Database”
RETURN n
Each condition in the query can be converted into the triple of (subject) - [verb] - (object) and unioned with the associated triple. Triples from the above queries are (n, taughtBy, m) and (m, interestField, Database). Remove triple (m:Professor, hasInterestField, Database) from the query will obtain the following new query:
MATCH (n:Student) - [r:TaughtBy] - (m:Professor)
RETURN n

Example 2:
Graph query:
MATCH (n:Student) - [r:TaughtBy] - (m:Professor)
WHERE m.interestField = “Database”
UNION (n:Student) - [:hasStanding] - (Sophomore)
RETURN n
Each condition in the query can be considered into the triple of (subject) - [verb] - (object) and unioned with the associated triple. Triples from the above queries are (n, taughtBy, m), (m, interestField, Database), (n, hasStanding, Sophomore). Remove triple (n:Student, taughtBy, m:Professor) from the query will obtain the following 2 new queries:
MATCH (m:Professor) - [:hasInterestField] - (Database)
RETURN m
And
MATCH (n:Student) - [:hasStanding] - (Sophomore)
RETURN n

Based on 2 provided examples, solve the following task:
Each condition in the query can be considered the triple of (subject) - [verb] - (object). 
Do not negate the condition if it is removed. Remove triple {triple} from the following query:
{query}
Only return result query after removing the triple.
"""

adjusting_prompt = """
A user with limited knowledge of graph queries and knowledge graphs writes a triple in the form of (subject, relationship, object) to query a knowledge graph:

(m:Professor)-[:interestField]-(Text Processing)

However, the triple might not be correct to match any existing triple in the knowledge graph. Let's consider some closely related transformations of the entities and relationship in the triple:

(Text Processing) might be (Natural Language Processing), (Text Parser), (String Manipulation)
(interestField) might be (ResearchFocus)
(String Manipulation) - [isTopicOf] - (CSDS 310)
(Natural Language Processing) - [:researchFocus] - (:Professor)
(CSDS 310) - [taughtBy] - (Professor)
Step by step reason about closely related facts from the knowledge graph and if and only if it is necessary,  based on that, adjust the entities, relationship, and even the triple itself that is most related to the original query. Finally, give me the final adjusted triple:
Answer:
The query is matching a professor who has an interest in Text Processing. From a closely related transformation, (Text Processing) might be (Natural Language Processing), (Text Parser), or (String Manipulation). (interestField) might be (ResearchFocus). So a professor who has an interest in Text Processing might alternatively mean a professor with a research focus in Natural Language Processing. 
(String Manipulation) - [isTopicOf] - (CSDS 310) means String Manipulation is a topic of CSDS 310, and  (CSDS 310) - [taughtBy] - (Professor) means CSDS 310 is taught by a professor, so combining them together mean String Manipulation is a topic of CSDS 310 taught by a professor. So a professor who has an interest in Text Processing might alternatively mean he is teaching CSDS 310 that has a topic String Manipulation.
A professor who has an interest in Text Processing is more semantically similar to a professor who has a research focus in Natural Language Processing, than a professor who teaches CSDS 310 that has the topic String Manipulation. Therefore, the original triple can be adjusted as:

(Natural Language Processing) - [:researchFocus] - (:Professor)

Task:
"""