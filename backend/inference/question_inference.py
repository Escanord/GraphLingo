import argparse
import heapq
import requests
import os
import time
import numpy.ma as ma
from dotenv import load_dotenv
from utils.knowledge_graph_helper import (
    retrieve_question_triples, 
    get_node_attributes,
    get_popularity,
)
from inference.exact_matching import get_exact_matching_facts
from inference.similarity_matching import diversified_similarity_matching_agent as ds_matching_agent
from inference.antique import str2bool
from inference.similarity_inference import (
    similarity_score,
    cosine_score,
    embedding,
)
from query_decomposition.graph_query_decomposition import (
    transform,
)
from utils.session_storage import session_storage
from utils.prompts import suggestion_example_prompt

load_dotenv()
GPTKey = os.getenv('GPTKey')
# edge_popularity = get_popularity()

def get_top_attributes(attributes, triples, k):
    top_attrs = []

    for e1, rel, e2 in triples:
        for attribute in attributes:
            sim_score = max(similarity_score(e1, attribute['nodeType'] + attribute['propertyName']),
                            similarity_score(e2, attribute['nodeType'] + attribute['propertyName']))
            heapq.heappush(top_attrs, (sim_score, attribute))
            if (len(top_attrs) > k):
                heapq.heappop(top_attrs)
    top_attrs.sort(reverse=True)
    
    return [attr[1] for attr in top_attrs]


def build_prompt(args, question):
    """
    generate a prompt with relevant information to the input question
    Args:
        question: question to get information

    Returns:
        a prompted question
    """
    prompt = ''
    suggested_edges = ''
    old_storage = session_storage()
    new_storage = session_storage()
    if args.followup:
        old_storage = session_storage('./session_data/session.txt')
    
    triples = retrieve_question_triples(question)
    # triples = [['?', 'should take', 'courses for graph knowledge']]
    if len(ma.shape(triples)) < 2:
        triples = [triples]
    # triples = transform(triples)
    print(triples)
    attributes = get_node_attributes(args)
    top_attributes = get_top_attributes(attributes, triples, 10)
    final_nodes = []
    final_edges = []

    # try exact matching first
    facts, final_nodes, final_edges = get_exact_matching_facts(args, new_storage, top_attributes, triples)
    print(facts)
    if (len(facts) > 0):
        for k, v in facts.items():
            if len(prompt) < 3000:
                prompt = prompt + k + ' ' + v + '\n'
    
    # print(prompt)
    matching_agent = ds_matching_agent(args, triples, old_storage, new_storage)
    # if there is still space in the prompt
    if len(prompt) < 3000:
        print('Similarity matching facts process is running')
        facts, nodes, edges = matching_agent.get_sim_matching_facts(top_attributes, lambda_value=args.explorative_rate)
        final_nodes += nodes
        final_edges += edges

        for k, v in facts.items():
            if len(prompt) < 3000:
                prompt = prompt + k + ' ' + v + '\n'
    prompt = 'Context:' + '\n' + prompt + '\n' + question + '\n'

    # get the prompt used for question suggestion
    start = time.time()
    suggested_prompt = ''
    onto_suggested_prompt = ''
    suggested_edges, onto_suggested_edges = matching_agent.get_exploration_triples()
    end = time.time()
    print(f"get exploration triples process took: {end - start} seconds")
    start = time.time()
    for triple in suggested_edges:
        if len(suggested_prompt) < 3000:
            e1 = ' '.join(str(k) + ':' + str(v) for k,
                         v in triple[0].items())
            e2 = ' '.join(str(v) + ',' for k,
                            v in triple[2].items())
            suggested_prompt = suggested_prompt + '[' + e1 + ', ' + triple[1] + ', ' + e2 + ']' + '\n'
    suggested_prompt = 'Given these triples: ' + suggested_prompt + '\n' + ' Suggest me 3 follow-up questions \
                        that must ask about 3 of the previous triples, \
                        and they should be in the following format:'
    suggested_prompt += '\n' + suggestion_example_prompt
    end = time.time()
    print(f"constructing suggestion prompt process took: {end - start} seconds")

    # get the prompt used for question suggestion onto-based
    for triple in onto_suggested_edges:
        if len(onto_suggested_prompt) < 3000:
            if type(triple[0]) is str:
                e =  ' '.join(str(v) + ',' for k,
                            v in triple[2].items())
                if 'has' not in triple[1]:
                    s = triple[0] + ' of ' + e + '\n'
                else:
                    s = triple[0] + f' {triple[1]} ' + e + '\n'
            else:
                e = ' '.join(str(k) + ':' + str(v) for k,
                         v in triple[0].items())
                if 'has' not in triple[1]:
                    s = triple[2] + ' of ' + e + '\n'
                else:
                    s = triple[2] + f' {triple[1]} ' + e + '\n'
            if len(s) <= 300:
                onto_suggested_prompt += s
    
    onto_suggested_prompt = 'Suggest me 3 follow-up questions \
                        that must ask about 3 of the following:' +\
                        onto_suggested_prompt + \
                        'and they should be in the following format:' + '\n'
    onto_suggested_prompt += suggestion_example_prompt
            
    if args.save_session:
        new_storage.save_graph('./session_data/session.txt')
    
    # print(prompt)
    # print(suggested_prompt)
    return prompt, suggested_prompt, onto_suggested_prompt, final_nodes, final_edges


def get_answer(question):
    request_body = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 800,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "messages": [{
            "role": "user",
            "content": question,
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


def main(args):
    start = time.time()

    question = args.question
    print(question)
    question, suggested_prompt, onto_prompt, nodes, edges = build_prompt(args, question)
    print(question)
    answer = get_answer(question)
    questions = get_answer(suggested_prompt)
    suggestions = []
    for suggestion in questions.split('\n')[::1]:
        if len(suggestion.split(':')) == 2:
            suggestions.append(suggestion.split(':')[1])
    print(answer)
    questions += '\n' + get_answer(onto_prompt)
    print('Suggested follow-up questions:', '\n')
    answer += '\n' + 'You might also be interested in asking these questions:'
    print(questions)
    end = time.time()
    print(f"The process took: {end - start} seconds")
    return answer, suggestions, nodes, edges


if __name__ == "__main__":
    # Input flags
    parser = argparse.ArgumentParser(description='Virtual Assistant System')
    parser.add_argument('--save_session', type=str2bool, default=False)
    parser.add_argument('--followup', type=str2bool, default=False)
    parser.add_argument('--question', type=str, default='What courses should I take for data management knowledge?')
    parser.add_argument('--kg', type=str, default='neo4j')
    args = parser.parse_args()
    args.explorative_rate = 0.001
    main(args)
# What datasets have samples with a peak between 24 and 30?
