from utils.knowledge_graph_helper import (
    get_exact_matching_nodes,
    find_lca,
    get_path,
    update_triples_info,
    get_k_hops_graph,
    get_path_ids,
    get_triple_properties
)


def get_exact_matching_facts(args, storage, top_attributes, triples):
    """
    get exact matching facts from the knowlege graph against the input triples
    Args:
        top_attributes: top entity's attributes that are relevant to the entities from the questions
        triples: triples from the questions

    Returns:
        a dictionary of exact match facts from the knowledge graph
    """
    facts = {}
    nodes = []
    edges = []
    nodes_checker = {}
    ids = get_exact_matching_nodes(triples, top_attributes)
    # gather info around exactly matched nodes
    for id in ids:
        sub_graph = get_k_hops_graph(id, 1)
        update_triples_info(facts, sub_graph)
        for triple in sub_graph:
            storage.insert_triple([triple['id(n)'], triple['id(r)'], triple['id(m)']])

            # add nodes and edges to visualize
            ids = [triple['id(n)'], triple['id(r)'], triple['id(m)']]
            properties = get_triple_properties(triple['id(n)'], triple['id(r)'], triple['id(m)'])
            if str(ids[0]) not in nodes_checker:
                    nodes_checker[str(ids[0])] = 1
                    id = ids[0]
                    node = {
                        'id': str(id),
                        'name': properties['n.name'],
                        'group': properties['labeln']
                    }
                    nodes.append(node)

            if str(ids[2]) not in nodes_checker:
                nodes_checker[str(ids[2])] = 1
                id = ids[2]
                node = {
                    'id': str(id),
                    'name': properties['m.name'],
                    'group': properties['labelm']
                }
                nodes.append(node)
            
            edge = {
                'name': properties['type(r)'],
                'source': str(ids[0]),
                'target': str(ids[2])
            }
            edges.append(edge)

            
    #BANKS algo
    lca_id, path_len = find_lca(ids)
    if lca_id is not None:
        for id in ids:
            if id != lca_id:
                path = get_path(lca_id, id, path_len)
                if path is not None:
                    for i, element in enumerate(path):
                        if i % 2 == 1:
                            update_triples_info(facts, [{'properties(n)': element[0], 'type(r)': element[1], 'properties(m)': element[2]}])
                            
                    path_ids = get_path_ids(lca_id, id, path_len)
                    for i, element in enumerate(path_ids):
                        if i % 2 == 1:
                            storage.insert_triple([path_ids[i - 1], path_ids[i], path_ids[i + 1]])
                            # add nodes and edges to visualize
                            ids = [path_ids[i - 1], path_ids[i], path_ids[i + 1]]
                            properties = get_triple_properties(path_ids[i - 1], path_ids[i], path_ids[i + 1])
                            if ids[0] not in nodes_checker:
                                    nodes_checker[ids[0]] = 1
                                    id = ids[0]
                                    node = {
                                        'id': str(id),
                                        'name': properties['n.name'],
                                        'group': properties['labeln']
                                    }
                                    nodes.append(node)

                            if ids[2] not in nodes_checker:
                                nodes_checker[ids[2]] = 1
                                id = ids[2]
                                node = {
                                    'id': str(id),
                                    'name': properties['m.name'],
                                    'group': properties['labelm']
                                }
                                nodes.append(node)
                            
                            edge = {
                                'name': properties['type(r)'],
                                'source': str(ids[0]),
                                'target': str(ids[2])
                            }
                            edges.append(edge)
                            
    # print(facts)
    return facts, nodes, edges