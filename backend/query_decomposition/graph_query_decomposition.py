import os
import time
import requests
import ast
from dotenv import load_dotenv
from collections import defaultdict

from utils.knowledge_graph_helper import (
    get_nodes,
    get_path,
    get_neighbor_relations,
    get_path_ids
)

from utils.prompt_describer import (
    describe_neighbors,
    describe_examples,
    describe_task,
    describe_triples,
    describe_node,
    describe_transformed_result
)

from query_decomposition.transfomation.transformation_function import transformations

load_dotenv()
GPTKey = os.getenv('GPTKey')
nodes = get_nodes()

def get_answer(prompt):
    request_body = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 1000,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "messages": [{
            "role": "user",
            "content": prompt,
        }]
    }

    request_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GPTKey}',
    }

    response = requests.post('https://api.openai.com/v1/chat/completions',
                             json=request_body, headers=request_headers, timeout=60)

    # print(response.json())
    return response.json()["choices"][0]["message"]['content']

def get_transformation_matches(transformation_functions, entity):
    matches = defaultdict(lambda: [])

    for node in nodes:
        for func in transformation_functions:
            id = node[0]
            for key, val in node[1].items():
                if func(val) == entity:
                    matches[func.__qualname__.split('.')[0]].append((id, key, val))
                    break
    
    return matches

def get_examples(h, t):
    h_matches = get_transformation_matches(transformations, h)
    t_matches = get_transformation_matches(transformations, t)
    examples = []
    candidate_node_ids = []

    for h_trans, h_nodes in h_matches.items():
        for h_match in h_nodes:
            for t_trans, t_nodes in t_matches.items():
                for t_match in t_nodes:
                    path = get_path(h_match[0], t_match[0], 2)
                    id_path = get_path_ids(h_match[0], t_match[0], 2)
                    example = []
                    if path is not None:
                        # append (node_id, node_name)
                        candidate_node_ids.extend([
                            (id_path[0], path[0][list(path[0].keys())[0]]), 
                            (id_path[-1], path[-1][list(path[-1].keys())[0]])
                        ])
                        for id, element in enumerate(path):
                            if id % 2 == 1:
                                example.append(str((element[0][list(element[0].keys())[0]], element[1], element[2][list(element[2].keys())[0]])))
                        examples.append(example)

    return examples, candidate_node_ids

def describe_nodes(candidates):
    description = ""

    for node, name in candidates:
        neighbors = defaultdict(lambda: [])
        neighbor_relations = get_neighbor_relations(node)
        for relation, element in neighbor_relations:
            neighbors[relation].append(element)
        description += describe_neighbors(name, neighbors)

    return description

def describe_entity_with_queries(entity, q, q_prime, transformed_value):
    neighbors = []
    prime_value = None
    # for triple in q:
    #     if triple[0] == entity or triple[2] == entity:
    #         neighbors.append(triple)

    for triple in q_prime:
        if triple[0] in transformed_value and transformed_value[triple[0]] == entity:
            prime_value = triple[0]
            neighbors.append((triple[0], triple[1], triple[2]))
        if triple[2] in transformed_value and transformed_value[triple[2]] == entity:
            prime_value = triple[2]
            neighbors.append((triple[0], triple[1], triple[2]))

    return describe_triples(entity, neighbors) + (describe_transformed_result(entity, prime_value) if prime_value is not None else "")

def construct_transformation_prompt(triple, q, q_prime, transformed_values):
    #get examples
    example_triples, candidate_node_ids = get_examples(triple[0], triple[2])
    examples = "Examples: \n"
    h_matches = get_transformation_matches(transformations, triple[0])
    t_matches = get_transformation_matches(transformations, triple[2])
    h_structure = describe_entity_with_queries(triple[0], q, q_prime, transformed_values)
    t_structure = describe_entity_with_queries(triple[2], q, q_prime, transformed_values)
    examples += describe_node(triple[0], h_matches, h_structure)
    examples += describe_node(triple[2], t_matches, t_structure)
    examples += describe_examples(triple, example_triples)
    if examples == "Examples: \n":
        examples = ''


    # get context
    context = "Context: \n"
    context += describe_nodes(candidate_node_ids)
    if context == "Context: \n":
        context = ''
    task = describe_task(triple)

    return context + examples + task, examples != ''

def transform(q):
    def parse_answer(answer):
        tokens = answer.split('\n')
        i = 1
        while i < len(tokens) and '[' not in tokens[-i] and ']' not in tokens[-i]:
            i += 1
        while tokens[-i][0] != '[':
            tokens[-i] = tokens[-i][1:]
        while tokens[-i][-1] != ']':
            tokens[-i] = tokens[-i][:-1]
        return ast.literal_eval(tokens[-i])

    q_prime = []
    transformed_values = {}

    while q:
        triple = q[0]
        prompt, has_examples = construct_transformation_prompt(triple, q, q_prime, transformed_values)
        print(prompt)
        if has_examples:
            answer = get_answer(prompt)
            print(answer)
            triples = parse_answer(answer)
        else:
            triples = [triple]
        q_prime.extend(triples)
        transformed_values[triples[0][0]] = triple[0]
        transformed_values[triples[-1][-1]] = triple[2]
        q.remove(triple)
    
    return q_prime
    


def main(args):
    start = time.time()
    query = args['query']
    transformation_prompt = construct_transformation_prompt(query, query)
    end = time.time()
    print(f"The process took: {end - start} seconds")

if __name__ == "__main__":
    # args = {}
    # args['query'] = '''
    #                 MATCH (c:Course) - [:hasTopic] - (t:Topic)
    #                 WHERE t.name = “Machine Learning”
    #                 UNION (c) - [:taughtBy] - [p:Professor]
    #                 WHERE p.from = “CS Department”
    #                 AND p.title = “assistant professor”
    #                 RETURN c
    #                 '''
    # main(args)

    # prompt = """
    # Context:
    # Given a subgraph in this (entity1, relationship, entity2) format:
    #     (?:Student, take, CSDS 234)
    #     (CSDS 234, taught by, professor Wu)
    #     (CSDS 234, from, CSDS Department)
    #     (professor Wu, from, CSDS Department)
    #     (professor Wu, has research interest, Knowledge Graph)
    # Transformation function can alter the entity, relationship, or even a triple into different representation.
    # The transformtation functions must maintain the triple in the format of (entity1, relationship, entity2).
    # The transformation functions must manintain the semantic meaning of the result, and the result should still make sense.
    # Example:
    # Some examples of graph transformtation functions such as shrinkage or abbreviation.
    #  - (Introduction to Java, offered in, CS Department)
    #     and
    #    (CS Department, in, School of Engineering) 
    #    can be transformed to 
    #    (Introduction to Java, offered in, School of Engineering) 
    #    by shrinking 2 relationships into 1 direct relationship.
    # - Entity (Mathematical department) can be transformed as (Math Dept)
    # Task:
    # Firstly, think of at least 8 transformation functions to modify the structure of the subgraph.
    # Then, use together at least 5 transformation functions to transform the original subgraph to obtain only one transformed subgraph.
    # Finally, only describe the transformed subgraph's triples in the format of (entity1, relationship, entity2).
    # """
    # print(get_answer(prompt))

    # prompt = """
    # Example:
    # Given a subgraph:
    #     (CSDS 234, taught by, professor Wu)
    #     (CSDS 234, from, CSDS department)
    #     (CSDS 234, hasTopic, structured and unstructured data)
    #     (CSDS 234, hasTopic, XML)
    #     (CSDS 234, hasCourseGoal, understanding data processing)
    #     (CSDS 234, hasCourseGoal, designing databases)
    #     (CSDS Department, has, professor Wu)
    #     (CSDS Department, has professor Xu)
    # A user write a graph query to retrieve information from that subgraph, but the user does not have enough query language knowledge and understanding of the graph,
    # the user write a query that cannot obtain result from the subgraph:
    #     - (?:Learner, learns from, professor Wu)
    # Each trasnformation function can be used on incorrect transformed entity in the query to match with correct entity from the subgraph.
    # The result of transformation function must match with the fact from the subgraph.
    # The transformation functions must manintain the semantic meaning of the result, and the result should still make sense.
    # Transformation functions:
    #     Abbreviation Reversal: (CSDS Department) can be transformed back to (CSDS Dept).
    #     Synonym Replacement Reversal: (take) can be transformed back to (enroll in).
    #     Reverse Relationship Reversal: (taught by) can be transformed back to (teaches).
    #     Expansion Reversal: (CSDS 234, from, CSDS Dept) and (professor Wu, from, CSDS Dept) can be transformed back to (CSDS 234, taught by, professor Wu).
    #     Entity Substitution Reversal: (Knowledge Graph) can be transformed back to (Graph of Knowledge).
    #     Relationship Substitution Reversal: (has research interest) can be transformed back to (focuses on).
    
    # The query can be rewritten by taking some knowledge from the subgraph and applying some transformation functions on the query to be able to query some results:
    #     (?:Student, take, CSDS 234)
    #     (CSDS 234, taughtBy, professor Wu)
    # Task:
    # Given a subgraph:
    #     (CSDS 293, from, CSDS department)
    #     (CSDS 293, hasTopic, functional programming)
    #     (CSDS 293, hasTopic, software design)
    #     (CSDS 293, hasCourseGoal, clean coding)
    #     (CSDS 293, hasCourseGoal, understanding software principles)
    #     (CSDS 293, hasCourseGoal, software design)
    #     (software design, isTopicOf, CSDS 393)
    #     (CSDS 293, taughtBy, professor Liberatore)
    #     (understanding software principles, isCourseGoal, CSDS 393)
    # and a query written by a user who do not have enough knowledge about query language and this subgraph:
    #     (software design, taughtBy, prof. Liberatore)
    # Firstly, think of at least 6 transformation functions that can modify the query to match with correct entity, relationship, and triple from the subgraph.
    # Each trasnformation function can be used to match correct entity from the subgraph, instead of the incorrect entity in the query.
    # The result of transformation function must match with the fact from the subgraph. The transformation functions must manintain the semantic meaning of the result, and the result should still make sense.
    # Then, use one or more the transformation functions to get the incorrect entities, relationships, and triples.
    # Fianlly, by using the transformation functions, rewrite the following query for me so it can query some result from the subgraph.
    # """
    # print(get_answer(prompt))

    # prompt = """
    # Reverse the behaviors of these transformation functions for me but do not change the name of the functions by any means. Give me the final result by listing functions in the same format.
    #     1. Abbreviation: (CSDS Department) can be transformed as (CSDS Dept)
    #     2. Synonym replacement: (take) can be transformed as (enroll in)
    #     3. Reverse relationship: (taught by) can be transformed as (teaches)
    #     4. Expansion: (CSDS 234, from, CSDS Dept) and (professor Wu, from, CSDS Dept) can be combined into (CSDS 234, taught by, professor Wu)
    #     5. Entity substitution: (Knowledge Graph) can be transformed as (Graph of Knowledge)
    #     6. Relationship substitution: (has research interest) can be transformed as (focuses on)
    # """
    # print(get_answer(prompt))
    # query = [("Learning", "taught in", "133"), ("Learning", "taught by", "Ray")]
    query = [("?", "more about", "Soumya Ray")]
    # print(transform([("Learning", "taught in", "133")]))
    print(transform(query))
    # print(construct_transformation_prompt(("M. L.", "has topic", "Learning"), q = [("M. L.", "has topic", "Learning")], q_prime = [('Naïve Bayes Classifiers', 'isTopicOf', ' Introduction to Artificial Intelligence  '), (' Introduction to Artificial Intelligence  ', 'taughtBy', ' Prof. Soumya Ray  ')]))