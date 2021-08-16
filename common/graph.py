'''Directed graph and associated algorithms.
'''
from collections import (defaultdict, deque)


class DirectedGraph:

    def __init__(self) -> None:
        '''Directed graph represented by adjacent list.'''
        #  initialize empty adjacency map: node -> [node1, node2, ...]
        self.__adjacency = defaultdict(list)

        # empty in degrees: node -> int
        self.__in_degrees = defaultdict(int)
    

    def __str__(self) -> str:
        '''Show adjacent list of graph.'''
        f = lambda node: str(node.id)
        items = [f'{node.id}: {",".join(map(f, node_list))}' for node, node_list in self.__adjacency.items()]
        return '\n'.join(items)


    def add_edge(self, node_from, node_to):
        '''Add a directed edge from `node_from` to `node_to`. 

        Args:
            node_from: Start node in user defined type.
            node_to: End node in user defined type.
        '''
        self.__adjacency[node_from].append(node_to)        

        # update in degree
        # NOTE: the in degree of source node is always zero
        if node_from not in self.__in_degrees:
            self.__in_degrees[node_from] = 0
        self.__in_degrees[node_to] += 1


    def sort(self) -> list:
        '''Sort nodes in topological order.
        '''
        res = []

        # collect nodes with zero in degree
        q = deque()
        in_degrees = {}
        for node, degree in self.__in_degrees.items():
            in_degrees[node] = degree # copy in degrees
            if degree==0:
                q.append(node)
        if not q: return [] # no valid topological order

        # bfs
        while q:
            node = q.popleft()
            res.append(node)

            for adj_node in self.__adjacency[node]:
                in_degrees[adj_node] -= 1
                if in_degrees[adj_node]==0: q.append(adj_node)
        
        # the in-degree of all nodes must be zero if the Topological Sorting is successful
        for node, in_degree in in_degrees.items():
            if in_degree!=0: return []
        
        return res
    

    def longest_path(self, node_from, node_to, fun_weight) -> float:
        '''Calculate the longest path length between two nodes.

        https://www.geeksforgeeks.org/find-longest-path-directed-acyclic-graph/

        Args:
            node_from: Start node.
            node_to: End node.
            fun_weight: Function handle taking the start node instance as input, returns a float 
                value representing the weight value of the associated edge.
        '''
        if node_from not in self.__adjacency or node_to not in self.__adjacency:
            raise Exception('Nodes not exist in current graph.')

        max_value = float('inf')
        min_value = float('-inf')

        # topological sort first
        sorted_nodes = self.sort()
        if not sorted_nodes: return max_value

        # initialize distances to all vertices as infinite and distance to source as 0
        dist = { node: min_value for node in self.__adjacency}
        dist[node_from] = 0.0

        # update distance based on sorted nodes
        for node in sorted_nodes:
            # always negative infinite if current distance is negative infinite
            if dist[node]==min_value: continue

            # unnecessary to move on if reaching target node
            if node==node_to: break

            # update distances of all adjacent vertices
            for adj_node in self.__adjacency[node]:
                new_length = dist[node] + fun_weight(adj_node)
                if dist[adj_node] < new_length:
                    dist[adj_node] = new_length
        
        return dist[node_to]