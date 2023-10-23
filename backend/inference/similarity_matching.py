import heapq
import time
import numpy as np
from collections import defaultdict
from utils.knowledge_graph_helper import (
    get_nodes_from_attrs,
    get_k_hops_graph,
    get_popularity,
    get_expanded_nodes_attrs,
    get_triple_properties,
    get_types,
)
from inference.similarity_inference import (
    cosine_score,
    embedding,
)
from utils.session_storage import session_storage


def get_top_k_nodes(data_nodes, triples, k):
        top_data_nodes = []
        embeddings = []

        entities = [triple[0] if triple[0] != '?' else triple[2] for triple in triples]
        embeddings = embedding(entities)
        
        for node in data_nodes:
            node_embedding = embedding(str(node[1]))
            similarity_score = 0
            for entity_embedding in embeddings:
                similarity_score = max(similarity_score, cosine_score(node_embedding, entity_embedding))
            heapq.heappush(top_data_nodes, (similarity_score, node))
            if len(top_data_nodes) > k:
                heapq.heappop(top_data_nodes)
        # top_data_nodes.sort(reverse=True)
        
        return [node[1] for node in top_data_nodes[:k]]


def get_representation(triple):
        if type(triple[0]) is dict:
            e1 = ' '.join(str(k) + ':' + str(v) for k,
                                v in triple[0].items())
            e2 = ' '.join(str(v) + ',' for k,
                                v in triple[2].items())
        else:
            e1 = triple[0]
            e2 = triple[2]

        return e1 + ' ' + triple[1] + ' ' + e2


class diversified_similarity_matching_agent:
    def __init__(self, args, question_triples, old_storage, cur_storage):
        self.question_triples = question_triples
        self.save_session = args.save_session
        self.followup = args.followup
        self.old_storage = old_storage
        self.cur_storage = cur_storage
        self.facts = {}
        self.rev_scores = {}
        self.triples_embedding = {}
        self.rep_to_triple = {}
        self.rep_to_id = {}
        self.question_triples_embedding = {}
        # result graph things
        self.result_graph = []
        self.result_graph_embedding = {}
        self.edge_popularity = get_popularity()
        self._pre_process()

    def _pre_process(self):
        for triple in self.question_triples:
            rep = get_representation((triple[0], triple[1], triple[2]))
            self.question_triples_embedding[rep] = embedding(rep)
            
        for triple in self.cur_storage.graph:
            properties = get_triple_properties(triple[0], triple[1], triple[2])
            triple_rep = get_representation((properties['properties(n)'], properties['type(r)'], properties['properties(m)']))
            self.triples_embedding[triple_rep] = self.result_graph_embedding[triple_rep] = triple_embedding = embedding(triple_rep)
            self.rev_scores[triple_rep] = self.get_rev_score(1, triple_embedding, self.result_graph_embedding, properties['type(r)'])
            self.rep_to_triple[triple_rep] = [properties['properties(n)'], properties['type(r)'], properties['properties(m)']]
            self.rep_to_id[triple_rep] = [triple[0], triple[1], triple[2]]
            self.result_graph.append(self.rep_to_id[triple_rep])

    def get_rev_score(self, dist, triple_embedding, graph_embedding, edge_type):
        type_popularity = self.edge_popularity[edge_type]
        
        return dist * np.average([cosine_score(triple_embedding, graph_triple) \
                                for _,graph_triple in graph_embedding.items()]) \
                    * type_popularity

    def max_sum_dispersion(self, update_fact = True, lambda_val = 0.001, k = 100):
        """
            MaxSumDispersion greedy algorithm to choose a subset of elements 
            that maximize the total diversification & relevance score.
        Args:
            facts: facts object to populate chosen triples into
            rev_scores: rev score of the facts
            triples_embeddings: embedding of the triples to choose from
            rep_to_triples: convert textual representation of a triple into triple form
            lambda_val (float, optional): lambda value of diversification degree. Defaults to 0.01.
            k (int, optional): maximum number of elements in the subset. Defaults to 100.
        """
        def update_fact(facts, triples):
            increased_len = 0
            
            for triple in triples:
                fact1 = ' '.join(str(k) + ':' + str(v) for k,
                            v in triple[0].items())
                fact2 = ' '.join(str(v) + ',' for k,
                                v in triple[2].items())

                try:
                    facts[fact1] = facts[fact1] + ' ' + triple[1] + ' ' + fact2 + ','
                except KeyError as error:
                    facts[fact1] = ' ' + triple[1] + ' ' + fact2
                    increased_len += len(fact1)
                increased_len += len(triple[1]) + len(fact2)
            
            return increased_len
            
        chosen = defaultdict(lambda:0)
        f = []
        embed_list = [(rep, embed) for rep, embed in self.triples_embedding.items()]
        for rep1, embed1 in embed_list:
            for rep2, embed2 in embed_list:
                if rep1 is not rep2:
                    score = self.rev_scores[rep1] + self.rev_scores[rep2] + 2 * lambda_val * (1 - cosine_score(embed1, embed2))
                    f.append((score, rep1, rep2))
                    
        f.sort(key=lambda x : x[0], reverse=True)
        prompt_len = 0
        num_chosen = 0
        for triple in f:
            if prompt_len >= 2800 or num_chosen >= k:
                break
            ids1 = self.rep_to_id[triple[1]]
            ids2 = self.rep_to_id[triple[2]]
            if chosen[triple[1]] > 0 or chosen[triple[2]] > 0 or \
            self.cur_storage.in_session(ids1[0], ids1[1], ids1[2]) or \
            self.cur_storage.in_session(ids2[0], ids2[1], ids2[2]):
                continue
            prompt_len += update_fact(self.facts if update_fact else {}, (self.rep_to_triple[triple[1]], self.rep_to_triple[triple[2]]))
            chosen[triple[1]] = 1
            chosen[triple[2]] = 1
            num_chosen += 2
        
        return chosen

    def get_exploration_triples(self, lambda_value = 0.8):
        self.triples_embedding = {}
        self.rev_scores = {}
        visited_edge = defaultdict(lambda:False)
        for edge in self.result_graph[:5]:
            k_hop_graph = get_k_hops_graph(edge[0], 1)
            k_hop_graph += get_k_hops_graph(edge[2], 1)
            for triple in k_hop_graph:
                if not self.cur_storage.in_session(triple['id(n)'], triple['id(r)'], triple['id(m)']) or not visited_edge[triple['id(r)']]:
                    visited_edge[triple['id(r)']] = True
                    triple_rep = get_representation((triple['properties(n)'], triple['type(r)'], triple['properties(m)']))
                    self.triples_embedding[triple_rep] = triple_embedding = embedding(triple_rep)
                    self.rep_to_triple[triple_rep] = [triple['properties(n)'], triple['type(r)'], triple['properties(m)']]
                    self.rep_to_id[triple_rep] = [triple['id(n)'], triple['id(r)'], triple['id(m)']]
                    self.rev_scores[triple_rep] = self.get_rev_score(1, triple_embedding, self.result_graph_embedding, triple['type(r)'])
                    
        chosen_edges = self.max_sum_dispersion(update_fact = False, lambda_val=lambda_value, k=10)
        suggested_edges = []
        onto_suggested_edges = []
        for edge, visited in chosen_edges.items():
            triple = self.rep_to_triple[edge]
            suggested_edges.append(triple)
            #TODO: convert head & tail of edges into onto and append to onto_suggested_edges
            ids = self.rep_to_id[edge]
            types = get_types(ids[0], ids[1], ids[2])
            onto_suggested_edges.append([triple[0], triple[1], types['labels(m)'][0]])
            onto_suggested_edges.append([types['labels(n)'][0], triple[1], triple[2]])
            
        return suggested_edges, onto_suggested_edges

    def get_sim_matching_facts(self, top_attributes, lambda_value = 0.001):
        """
        Retrieves diversifed triples from the knowledge graph that are most relevant to the question triples
        Args:
            top_attributes: top entity's attributes that are relevant to the entities from the questions
            question_triples: triples from the questions

        Returns:
            most diversified and relevant facts
            triples that to suggest follow-up questions
        """
        # if follow-up question, get_top_k_nodes from border nodes instead of data nodes, and then has section to also add previous graph's triples into the space of dispersion
        if self.followup:
            expanded_nodes = self.old_storage.get_nodes()
            data_nodes = get_expanded_nodes_attrs(expanded_nodes, top_attributes)
        else:
            data_nodes = get_nodes_from_attrs(top_attributes)
        start = time.time()
        top_data_nodes = get_top_k_nodes(data_nodes, self.question_triples, 10)
        end = time.time()
        print(f"Top-k nodes process took: {end - start} seconds")
        
        # perform similarity matching
        id2name = {}
        id2label = {}
        start = time.time()
        for node in top_data_nodes:
            id = node[0]
            sub_graph = get_k_hops_graph(id, 1)
            for triple in sub_graph:
                triple_rep = get_representation((triple['properties(n)'], triple['type(r)'], triple['properties(m)']))
                self.triples_embedding[triple_rep] = triple_embedding = embedding(triple_rep)
                self.rep_to_triple[triple_rep] = [triple['properties(n)'], triple['type(r)'], triple['properties(m)']]
                self.rep_to_id[triple_rep] = [triple['id(n)'], triple['id(r)'], triple['id(m)']]
                self.rev_scores[triple_rep] = self.get_rev_score(1, triple_embedding, self.question_triples_embedding, triple['type(r)'])
                # get id & name for visualization
                id2name[triple['id(n)']] = triple['n.name']
                id2label[triple['id(n)']] = triple['labeln']
                id2name[triple['id(m)']] = triple['m.name']
                id2label[triple['id(m)']] = triple['labelm']

        #choose the subset with maximum diversification & relevance scores
        end = time.time()
        print(f"Similarity matching process took: {end - start} seconds")


        start = time.time()
        chosen_edges_reps = self.max_sum_dispersion(lambda_val=lambda_value)
        end = time.time()
        print(f"Max-sum process took: {end - start} seconds")
        nodes = []
        edges = []
        nodes_checker = {}
        
        #----------------###------------------#
        #perform question suggestion
        for edge_rep, visited in chosen_edges_reps.items():
            if visited > 0:
                self.cur_storage.insert_triple(self.rep_to_id[edge_rep])
                ids = self.rep_to_id[edge_rep]
                triple = self.rep_to_triple[triple_rep]
                self.result_graph_embedding[edge_rep] = self.triples_embedding[edge_rep]
                self.result_graph.append(ids)

                # add nodes and edges to visualize
                if ids[0] not in nodes_checker:
                    nodes_checker[ids[0]] = 1
                    id = ids[0]
                    node = {
                        'id': str(id),
                        'name': id2name[id],
                        'group': id2label[id]
                    }
                    nodes.append(node)

                if ids[2] not in nodes_checker:
                    nodes_checker[ids[2]] = 1
                    id = ids[2]
                    node = {
                        'id': str(id),
                        'name': id2name[id],
                        'group': id2label[id]
                    }
                    nodes.append(node)
                
                edge = {
                    'name': triple[1],
                    'source': str(ids[0]),
                    'target': str(ids[2])
                }
                edges.append(edge)


        
        # print(rev_scores)
        # print(facts)
        # suggested_edges = []
        return self.facts, nodes, edges