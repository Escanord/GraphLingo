import requests
import os
import numpy as np
from ast import literal_eval
from dotenv import load_dotenv
from utils.prompts import question_entities_extraction_prompt
from neo4j import GraphDatabase
from collections import defaultdict
from utils.session_storage import session_storage

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


def retrieve_question_triples(text):
    request_body = {
        "model": "gpt-3.5-turbo-0125",
        "temperature": 0.3,
        "max_tokens": 800,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "messages": [{
            "role": "user",
            "content": question_entities_extraction_prompt + '\n'.join(text),
        }],
    }

    request_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GPTKey}',
    }

    response = requests.post('https://api.openai.com/v1/chat/completions',
                             json=request_body, headers=request_headers, timeout=60)

    entities = response.json()
    entities = entities['choices'][0]["message"]['content']
    entities = entities.split('\n')[-1]
    while len(entities) > 0 and entities[0] == ' ':
        entities = entities[1:]
    entities = literal_eval(entities)

    return entities


def get_node_attributes():
    def get_attributes(tx):
        attributes = tx.run('call db.schema.nodeTypeProperties()')
        return attributes.data()

    connect_dbms()
    with driver.session() as session:
        attributes = session.execute_read(get_attributes)
    close()
    return attributes


def get_node_labels():
    def get_labels(tx):
        labels = tx.run("""
                      MATCH (n) RETURN distinct labels(n)
                      """)
        result = []
        for label in labels.data():
            result.append(label['labels(n)'][0])
        return result

    connect_dbms()
    with driver.session() as session:
        labels = session.execute_read(get_labels)
    close()
    return labels


def get_onto_triples():

    def get_triples(tx):
        triples = tx.run("""
                      MATCH (n)-[r]->(m) RETURN distinct labels(n), type(r)
                      """)
        result = []
        for triple in triples:
            result.append((triple['labels(n)'][0], triple['type(r)']))

        triples = tx.run("""
                         MATCH (n)-[r]->(m) RETURN distinct type(r), labels(m)
                         """)
        for triple in triples:
            result.append((triple['type(r)'], triple['labels(m)'][0]))

        return result

    connect_dbms()
    with driver.session() as session:
        triples = session.execute_read(get_triples)
    close()
    return triples


def update_triples_info(facts, triples):
    '''
    Update the facts dictionary witn input list of triples and each triple 
    in the form of ('properties(n)': val1, 'type(r)': rel_type, 'properties(m)': val2)
    @facts: input fact dictionary to be updated
    @triples: the list of triples to inject into the facts dictionary
    '''
    for triple in triples:
        fact1 = ' '.join(str(k) + ':' + str(v) for k,
                         v in triple['properties(n)'].items())
        fact2 = ' '.join(str(v) + ',' for k,
                         v in triple['properties(m)'].items())

        try:
            facts[fact1] = facts[fact1] + ' ' + \
                triple['type(r)'] + ' ' + fact2 + ','
        except KeyError as error:
            facts[fact1] = ' ' + triple['type(r)'] + ' ' + fact2

    return facts


def get_exact_triples(facts, exact_triples, top_attrs):

    def get_triples(tx, exact_triples, top_attrs):
        for triple in exact_triples:
            for attr in top_attrs:
                nodeType = attr['nodeType'][2:len(attr['nodeType']) - 1]
                attr_name = attr['propertyName']
                entity = "'(?i).*" + (triple[0] if triple[0] !=
                                      '?' else triple[2]) + ".*'"

                triples = tx.run(
                    f'match (n:{nodeType})-[r]-(m) where n.{attr_name}  =~ {entity} return distinct properties(n),type(r),properties(m)')
                update_triples_info(facts, triples)

    connect_dbms()
    with driver.session() as session:
        session.execute_read(get_triples, exact_triples, top_attrs)

    close()
    

def get_exact_matching_nodes(question_triples, top_attrs):
    def get_nodes(tx, question_triples, top_attrs):
        result = []
        
        for triple in question_triples:
            for attr in top_attrs:
                nodeType = attr['nodeType'][2:len(attr['nodeType']) - 1]
                attr_name = attr['propertyName']
                entity = "'(?i).*" + (triple[0] if triple[0] !=
                                      '?' else triple[2]) + ".*'"
                nodes = tx.run(
                    f'match (n:{nodeType})-[r]-(m) where n.{attr_name}  =~ {entity} return distinct id(n)')
                
                for node in nodes:
                    data = node.data()
                    if data.get('id(n)') not in result:
                        result.append(data.get('id(n)'))
                    
        return result

    connect_dbms()
    with driver.session() as session:
        ids = session.execute_read(get_nodes, question_triples, top_attrs)

    close()
    return ids


def find_lca(ids):
    """
    BANKs implementation to find lca
    Args:
        ids: ids of nodes to find lca
    """
    def get_lca(tx, ids):
        str_ids = str(ids)
        lca = None
        len = None
        
        for i in range(1, 5):
            query = f"with {str_ids} as ids \
                        match (n)-[r *..{i}]-(m) \
                        where id(n) in ids \
                        with n, collect(id(m))+id(n) as nodePerId \
                        with collect(nodePerId) as parents \
                        with reduce(commonPa = head(parents), pa in parents | \
                        apoc.coll.intersection(commonPa,pa)) as commonPa \
                        return commonPa "
            nodes = tx.run(query)
            nodes = nodes.data()
            # print(nodes.data()[0]['commonPa'])
            # print(nodes.data()[0]['commonPa'])
            if nodes[0]['commonPa']:
                lca = nodes[0]['commonPa'][0]
                len = i
                break
        
        return lca, len
    
    connect_dbms()
    with driver.session() as session:
        lca, len = session.execute_read(get_lca, ids)
    close()
    
    return lca, len


def get_path(h_id, t_id, len, connect = True):
    def get_path(tx, h_id, t_id, len):
        query = f"match path = (n)-[*..{len}]->(m) \
                    where id(n) = {h_id} \
                    and id(m) = {t_id} \
                    and id(n) <> id(m) \
                    return apoc.path.elements(path)"
        
        path = tx.run(query)
        path = path.data()
        if path:
            return path[0]['apoc.path.elements(path)']
        else:
            return None
    
    if connect:
        connect_dbms()
    with driver.session() as session:
        path = session.execute_read(get_path, h_id, t_id, len)
    if connect:
        close()

    return path

def get_path_ids(h_id, t_id, len, connect = True):
    def get_path(tx, h_id, t_id, len):
        query = f"match path = (n)-[*..{len}]->(m) \
                    where id(n) = {h_id} \
                    and id(m) = {t_id} \
                    with reduce(x = [], node in apoc.path.elements(path)| x + id(node)) as x \
                    return x"
        
        path = tx.run(query)
        path = path.data()
        if path:
            return path[0]['x']
        else:
            return None
    
    if connect:
        connect_dbms()
    with driver.session() as session:
        path = session.execute_read(get_path, h_id, t_id, len)
    if connect:
        close()

    return path

def get_factual_triples(facts, onto_triple):
    def get_triples(tx, onto_triple):
        triples = tx.run(
            f'MATCH (n)-[r:{onto_triple[1][0]}]-(m:{onto_triple[1][1]}) RETURN properties(n),type(r),properties(m)')
        update_triples_info(facts, triples)

    connect_dbms()
    with driver.session() as session:
        session.execute_read(get_triples, onto_triple)
    close()
    
def get_expanded_nodes_attrs(expanded_nodes, top_attributes):
    def get_nodes(tx, top_attrs):
        result = []
        checker = {}
        ids = str(expanded_nodes)
        
        for attr in top_attrs:
            node_type = attr['nodeType'][2:len(attr['nodeType']) - 1]
            attr_name = attr['propertyName']
            query = f"with {ids} as ids \
                    MATCH (n:{node_type}) \
                    WHERE id(n) in ids \
                    RETURN distinct id(n), n.{attr_name}"
            nodes = tx.run(query)
            for node in nodes:
                data = node.data()
                value = data.get(f'n.{attr_name}')
                id = data.get('id(n)')
                if (value != None and id not in checker):
                    result.append((id, value))
                    checker[id] = 1
        
        return result
        
    connect_dbms()
    with driver.session() as session:
        nodes = session.execute_read(get_nodes, top_attributes)
    close()
    
    return nodes

def get_nodes_from_attrs(top_attributes):
    def get_nodes(tx, top_attrs):
        result = []
        checker = {}
        
        for attr in top_attrs:
            node_type = attr['nodeType'][2:len(attr['nodeType']) - 1]
            attr_name = attr['propertyName']
            query = f"MATCH (n:{node_type}) RETURN distinct id(n), n.{attr_name}"
            nodes = tx.run(query)
            for node in nodes:
                data = node.data()
                value = data.get(f'n.{attr_name}')
                id = data.get('id(n)')
                if (value != None and id not in checker):
                    result.append((id, value))
                    checker[id] = 1
        
        return result
        
    connect_dbms()
    with driver.session() as session:
        nodes = session.execute_read(get_nodes, top_attributes)
    close()
    
    return nodes

def get_k_hops_graph(node_id, k):
    def get_graph(tx, node_id, k):
        query = f"MATCH (n)-[r]->(m) WHERE id(n) = {node_id} RETURN properties(n), type(r), properties(m), id(n), id(r), id(m), n.name, m.name, labels(n)[0] as labeln, labels(m)[0] as labelm"
        graph = tx.run(query)
        
        triples = graph.data()

        return triples
    
    connect_dbms()
    with driver.session() as session:
        graph = session.execute_read(get_graph, node_id, k)
    close()
    
    return graph

# print(get_k_hops_graph(142,1))

# def get_k_hops_graph(node_id, k):
#     def get_graph(tx, node_id, k):
#         query = f"MATCH (n)-[*{k}..{k}]->(m) WHERE id(n) = {node_id} RETURN id(m)"
#         nodes = tx.run(query)
#         ids = []
#         graph = []
#         checker = session_storage()
        
#         for node in nodes:
#             data = node.data()
#             ids.append(data.get('id(m)'))
            
#         for id in ids:
#             path = get_path(node_id, id, k, connect = False)
#             path_ids = get_path_ids(node_id, id, k, connect = False)
#             for i, (element, ids) in enumerate(zip(path,path_ids)):
#                 if i % 2 == 1 and not checker.in_session(path_ids[i - 1], path_ids[i], path_ids[i + 1]):
#                     edge = {'properties(n)': element[0], 'type(r)': element[1], 'properties(m)': element[2], \
#                             'id(n)': path_ids[i - 1], 'id(r)': path_ids[i], 'id(m)': path_ids[i + 1]}
#                     checker.insert_triple((path_ids[i - 1], path_ids[i], path_ids[i + 1]))
#                     graph.append(edge)
                
#         return graph
    
#     connect_dbms()
#     with driver.session() as session:
#         graph = session.execute_read(get_graph, node_id, k)
#     close()
    
#     return graph

def get_types(id_h, id_r, id_t):
    def _get_types(tx, id_h, id_r, id_t):
        query = f"MATCH (n)-[r]->(m) \
                WHERE id(n) = {id_h} AND id(m) = {id_t} \
                RETURN labels(n), labels(m)"
        
        types = tx.run(query)
        
        return types.data()[0]
        
    connect_dbms()
    with driver.session() as session:
        types = session.execute_read(_get_types, id_h, id_r, id_t)
    close()
    
    return types

def get_popularity():
    def get_proportion(tx):
        query = """
                MATCH ()-[relationship]->() 
                RETURN TYPE(relationship) AS type, COUNT(relationship) AS amount
                """
        stat = tx.run(query)
        
        stat = stat.data()
        total = np.sum([t['amount'] for t in stat])
        return {edge_stat['type'] : edge_stat['amount'] / total for edge_stat in stat}
            
        
    connect_dbms()
    with driver.session() as session:
        pop = session.execute_read(get_proportion)
    close()
    
    return pop

def get_triple_properties(id_n, id_r, id_m):
    def get_triple(tx, id_n, id_r, id_m):
        query = f"MATCH (n)-[r]->(m) \
                WHERE id(n) = {id_n} AND id(r) = {id_r} AND id(m) = {id_m} \
                RETURN properties(n), type(r), properties(m), id(n), id(r), id(m), n.name, m.name, labels(n)[0] as labeln, labels(m)[0] as labelm"
        triple = tx.run(query)
        
        return triple.data()[0]
    
    connect_dbms()
    with driver.session() as session:
        triple = session.execute_read(get_triple, id_n, id_r, id_m)
    close()
    
    return triple

def get_nodes():
    def query_nodes(tx):
        query = f"MATCH (n) \
                RETURN n, id(n)"
        nodes = tx.run(query)

        return [(node['id(n)'], node['n']) for node in nodes.data()]
    
    connect_dbms()
    nodes = []
    with driver.session() as session:
        nodes = session.execute_read(query_nodes)

    return nodes

def get_neighbor_relations(id):
    def query_relations(tx, id):
        query = f"MATCH (n)-[l]->(m) \
                    WHERE id(n) = {id} \
                    AND EXISTS(m.name) \
                    return distinct type(l), labels(m), m"
        relations = tx.run(query)

        # print(relations.data())
        return [(relation['type(l)'], relation['labels(m)'][0] + ' ' + relation['m']['name']) for relation in relations.data()]
    
    connect_dbms()
    relations = []
    with driver.session() as session:
        relations = session.execute_read(query_relations, id)

    return relations

# print(get_neighbor_relations(142))