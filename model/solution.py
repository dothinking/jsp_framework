'''Solution of Job-Shop Schedule Problem, especially the sequence of operations
assigned in each machine, and the deduced start time of each operation accordingly.
'''

import matplotlib.pyplot as plt
from model.domain import Operation
from ..common.graph import DirectedGraph
from .problem import JSProblem


class JSSolution:

    def __init__(self, problem:JSProblem) -> None:
        '''Initialize solution by copying all operations from `problem`.

        Args:
            problem (JSProblem): Problem to solve.
        '''
        self.__problem = problem
        self.__operations = [op.copy() for op in problem.operations]

        # operations in topological order
        self.__sorted_ops = None # type: list[Operation]
    

    @property
    def ops(self): return self.__operations


    @property
    def sorted_ops(self): return self.__sorted_ops

 
    def evaluate(self, op:Operation=None):
        '''Evaluate specified and succeeding operations of current solution, especially 
        work time. Generally the machine chain was changed before calling this method.
        '''
        # update topological order due to the changed machine chain
        self.__update_graph()
        if not self.__sorted_ops:
            raise Exception("Invalid solution due to recursive dependencies.")

        # the position of target process
        pos = 0 if op is None else self.__sorted_ops.index(op)
        
        # update process by the topological order
        for i in range(pos, len(self.__sorted_ops)):
            self.__sorted_ops[i].update_start_time()


    def makespan(self) -> float:
        '''Makespan of current solution. 
        Only available when the solution is feasible; otherwise None.
        '''
        return max(lambda op: op.end_time, self.__operations) if self.is_feasible() else None


    def is_feasible(self) -> bool:
        '''If current solution is valid or not. 
        Note to call this method after evaluating the solution.
        '''
        return bool(self.__sorted_ops)


    def plot(self):
        '''Plot Gantt chart with `matplotlib`.'''
        # set chart style
        fig, (gnt_job, gnt_machine) = plt.subplots(2,1, sharex=True)
        
        gnt_job.set(ylabel='Job', \
            yticks=range(len(self.__problem.jobs)), \
            yticklabels=[f'Job-{job.id}' for job in self.__problem.jobs])
        gnt_job.grid(which='major', axis='x', linestyle='--')
        
        gnt_machine.set(xlabel='Time', ylabel='Machine',\
            yticks=range(len(self.__problem.machines)), \
            yticklabels=[f'M-{machine.id}' for machine in self.__problem.machines])
        gnt_machine.grid(which='major', axis='x', linestyle='--')

        # plot gantt task
        self.__plot_from_job_view(gnt_job)
        self.__plot_from_machine_view(gnt_machine)

        # show figure
        plt.show()

 
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


    def __plot_from_job_view(self, gnt):
        '''Plot Gantt chart from job view.'''
        for op in self.__operations:
            gnt.barh(op.job.id, op.duration, left=op.start_time, height=0.5)
    

    def __plot_from_machine_view(self, gnt):
        '''Plot Gantt chart from machine view.'''
        for op in self.__operations:
            gnt.barh(op.machine.id, op.duration, left=op.start_time, height=0.5)


    
