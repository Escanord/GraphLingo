
def describe_neighbors(entity, neighbors):
    description = f"- Entity {entity} has relationships: \n"
    
    for relation, nodes in neighbors.items():
        description += relation
        for i, node in enumerate(nodes):
            description += f" {node}," if i < len(nodes) - 1 else f" {node}\n"
    
    return description

def describe_triples(entity, neighbors):
    description = f"- Entity {entity} has neiborhood graph structure: \n"
    for triple in neighbors:
        # description += f"{e1} {l} {e2} \n"
        description += f"{str(triple)} \n"
    
    return description

def describe_transformed_result(entity, transformed_result):
    return f"{entity} is {transformed_result} \n"

def describe_examples(triple, examples):
    if len(examples) == 0:
        return ""
    example_description = f"Example triple transformations that the given triple can transform into: \n - To be able to retrieve result from the knowledge graph, triple {str(triple)} should be transformed into one of the following example triples of paths: \n "
    
    for example in examples:
        desc = " - A path: " if len(example) > 1 else " - A triple: "
        for i, triple in enumerate(example):
            desc += f" {str(triple)}," if i < len(example) - 1 else f" {str(triple)}.\n"
        example_description += desc

    return example_description

def describe_node(entity, matches, structure):
    if len(matches.items()) == 0:
        return ""
    node_example_description = f"- To be able to retrieve result from the knowledge graph, {entity} should be transformed into one of the following example entities: "
    for trans, nodes in matches.items():
        for match in nodes:
            node_example_description += f"{match[2]}, "
    node_example_description += '\n'
    return node_example_description + structure

def describe_task(triple):
    task = f"Task: \n Given a graph triple {str(triple)}.\n \
    Now, based on the provided graph structure context and the examples, perform the following tasks: \n \
    - Step by step reason about each entity's transformation example. \n \
    - Then use it to reason about provided transformation examples that the given triple can transform into. \n \
    - Combine all reasoning together to determine only one best transformation result. \n \
    The best result should: \n \
    - be able query some results from the knowledge graph. \n \
    - try maintain the entities' neighborhood structure. \n \
    End your answer by giving me only one best result in the form of a Python list: [('first entity', 'relationship', 'second entity'), ...] on one single line that can be parsed into an array of triples. Do not give me any note or warning after giving me the final result."
    
    return task

# step by step reason about each entity's example transformation, then apply it onto the entities within triple's example transformations.