'''Solution of Job-Shop Schedule Problem, especially the sequence of operations
assigned in each machine, and the deduced start time of each operation accordingly.
'''

from model.domain import Operation
from ..common.graph import DirectedGraph
from .problem import JSProblem


class JSSolution:

    def __init__(self, problem:JSProblem) -> None:
        '''Initialize solution by copying all operations from `problem`.

        Args:
            problem (JSProblem): Problem to solve.
        '''
        self.__operations = [op.copy() for op in problem.operations]

        # operations in topological order
        self.__sorted_ops = None # type: list[Operation]
    

    @property
    def ops(self): return self.__operations


    @property
    def sorted_ops(self): return self.__sorted_ops

 
    def evaluate(self) -> list:
        '''Evaluate current solution: update topological order and start time of each operation.'''
        pass


    def makespan(self) -> float:
        '''Makespan of current solution. 
        Only available when the solution is feasible; otherwise None.
        '''
        return max(lambda op: op.end_time, self.__operations) if self.is_feasible() else None


    def is_feasible(self) -> bool:
        '''If current solution is valid or not. 
        Note to call this method after evaluating the solution.
        '''
        pass

    
    def __update_graph(self):
        '''Update the associated directed graph and the topological order accordingly.'''
        # add the dummy source and sink node
        source = Operation(id=-1, machine=None, duration=0)
        sink = Operation(id=-1, machine=None, duration=0)

        # identical directed graph
        graph = DirectedGraph()
        for op in self.__operations:
            # job chain edge
            if op.pre_job_op is None:
                graph.add_edge(source, op)
            
            if op.next_job_op:
                graph.add_edge(op, op.next_job_op)
            else:
                graph.add_edge(op, sink)
            
            # machine chain edge
            if op.next_op and op.next_op!=op.next_job_op:
                graph.add_edge(op, op.next_op)

        # topological order:
        # except the dummy source and sink nodes
        ops = graph.sort()
        self.__sorted_ops = ops[1:-1] if ops else None


    


    
