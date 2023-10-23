from distutils.util import strtobool
import heapq
from utils.knowledge_graph_helper import get_factual_triples

def get_potential_labels(labels, entities, k):
    top_labels = []

    for entity in entities:
        for label in labels:
            similarity_score = similarity_score(entity, label)
            heapq.heappush(top_labels, (similarity_score, label))
            if (len(top_labels) > k):
                heapq.heappop(top_labels)

    return top_labels


def get_top_onto_triples(triples, onto_triples, k):
    top_triples = []

    for triple in triples:
        for onto_triple in onto_triples:
            similarity_score = similarity_score(
                ' '.join(triple[1:]), ' '.join(onto_triple))
            heapq.heappush(top_triples, (similarity_score, onto_triple))
            if (len(top_triples) > k):
                heapq.heappop(top_triples)

    return top_triples


def get_facts(onto_triples):
    facts = {}
    for triple in onto_triples:
        get_factual_triples(facts, triple)
    return facts


def get_relevant_facts(facts, triples):
    scores = {}
    for key in facts.keys():
        for triple in triples:
            similarity_score = similarity_score(key, ' '.join(triple[1:]))
            if key not in scores or similarity_score > scores[key]:
                scores[key] = similarity_score

    # attribute_name might add noise to the similarity comparision
    result = list(zip(scores.values(), scores.keys()))
    result.sort(reverse=True)

    # print(result)

    return result

def str2bool(x):
    """
    hack to allow wandb to tune boolean cmd args
    :param x: str of bool
    :return: bool
    """
    if type(x) == bool:
        return x
    elif type(x) == str:
        return bool(strtobool(x))
    else:
        raise ValueError(f'Unrecognised type {type(x)}')