from collections import defaultdict

class session_storage:
    def __init__(self, session_dir = None):
        self.graph = []
        self.visited = defaultdict(lambda:0)
        if session_dir is not None:
            self.read_graph(session_dir)
            
    def insert_triple(self, triple):
        self.visited[triple[1]] = 1
        self.graph.append([triple[0], triple[1], triple[2]])
        
    def delete_triple(self, edge):
        self.visited[edge] = 0
        for i, triple in enumerate(self.graph):
            if triple[1] == edge:
                self.graph.pop(i)
                break
    
    def in_session(self, h, edge, t):
        for triple in self.graph:
            if triple[0] == h and triple[2] == t:
                return True
            if triple[0] == t and triple[2] == h:
                return True
        return self.visited[edge] > 0
    
    def get_border_nodes(self):
        result_ids = []
        degree = defaultdict(lambda:0)
        for edge in self.graph:
            degree[edge[0]] += 1
            degree[edge[2]] += 1
        
        for node_id, deg in degree.items():
            if degree < 2:
                result_ids.append(node_id)
        
        return result_ids
    
    def get_nodes(self):
        nodes = []
        
        for edge in self.graph:
            if edge[0] not in nodes:
                nodes.append(edge[0])
            if edge[2] not in nodes:
                nodes.append(edge[2])
                
        return nodes
    
    def save_graph(self, dir):
        with open(dir, 'w') as file:
            for id, triple in enumerate(self.graph):
                file.write(str(triple[0]) + ' ' + str(triple[1]) + ' ' + str(triple[2]))
                if id < len(self.graph) - 1:
                    file.write('\n')

    def read_graph(self, dir):
        with open(dir, 'r') as file:
            for row in file:
                row = row.split(' ')
                self.visited[int(row[1])] = 1
                self.graph.append([int(row[0]), int(row[1]), int(row[2])])
