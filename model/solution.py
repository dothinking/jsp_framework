'''Solution of Job-Shop Schedule Problem, especially the sequence of operations
assigned in each machine, and the deduced start time of each operation accordingly.
'''

from collections import defaultdict
from matplotlib.container import BarContainer
from .domain import Operation
from .variable import OperationStep
from common.graph import DirectedGraph
from .problem import JSProblem


class JSSolution:

    def __init__(self, problem:JSProblem) -> None:
        '''Initialize solution by copying all operations from `problem`.

        Args:
            problem (JSProblem): Problem to solve.
        '''
        self.__ops = [OperationStep(op) for op in problem.ops]

        # initialize job chain
        self.__create_job_chain()

        # operations in topological order: available for disjunctive graph model only
        self.__sorted_ops = None # type: list[OperationStep]
    

    @property
    def ops(self): return self.__ops

    @property
    def sorted_ops(self): return self.__sorted_ops

    @property
    def makespan(self) -> float:
        '''Makespan of current solution. 
        Only available when the solution is feasible; otherwise None.
        '''
        return max(map(lambda op: op.end_time, self.__ops)) if self.is_feasible() else None


    def is_feasible(self) -> bool:
        '''If current solution is valid or not. 
        Note to call this method after evaluating the solution if based on disjunctive graph model.
        '''
        # check topological order if disjunctive graph model, 
        # otherwise check the start time further directly
        if self.__sorted_ops: return True

        # validate job chain
        job_chains = defaultdict(list)
        for op in self.__ops:
            job_chains[op.source.job].append(op)
        
        for job, ops in job_chains.items():
            ops.sort(key=lambda op: op.id) # sort in job sequence, i.e. default id order
            ref = 0
            for op in ops:
                if op.end_time <= ref: return False
                ref = op.end_time
        
        # validate machine chain
        machine_chains = defaultdict(list)
        for op in self.__ops:
            machine_chains[op.source.machine].append(op)
        
        for machine, ops in machine_chains.items():
            ops.sort(key=lambda op: op.start_time) # sort by start time
            ref = 0
            for op in ops:
                if op.end_time <= ref: return False
                ref = op.end_time
        
        return True


    def evaluate(self, op:Operation=None) -> bool:
        '''Evaluate specified and succeeding operations of current solution, especially 
        work time. Generally the machine chain was changed before calling this method.

        NOTE: this method is only available for disjunctive graph model.

        Args:
            op (Operation, optional): The operation step to update. Defaults to None,
                i.e. the first operation.
        
        Returns:
            bool: True if current solution is feasible.
        '''
        # update topological order due to the changed machine chain
        self.__update_graph()
        if not self.__sorted_ops: return False

        # the position of target process
        pos = 0 if op is None else self.__sorted_ops.index(op)
        
        # update process by the topological order
        for i in range(pos, len(self.__sorted_ops)):
            self.__sorted_ops[i].update_start_time()
        
        return True


    def plot(self, axes:tuple):
        '''Plot Gantt chart.

        Args:
            axes (tuple): Axes of `matplotlib` figure: (job sub-plot axis, machine sub-plot axis).
        '''
        gnt_job, gnt_machine = axes

        # title
        gnt_job.set_title(f'Result: {self.makespan or "n.a."}', color='gray', fontsize='small', loc='right')

        # clear plotted bars
        bars = [bar for bar in gnt_job.containers if isinstance(bar, BarContainer)]
        bars.extend([bar for bar in gnt_machine.containers if isinstance(bar, BarContainer)])
        for bar in bars: 
            bar.remove()
        
        # plot new bars
        for op in self.__ops:
            gnt_job.barh(op.source.job.id, op.source.duration, left=op.start_time, height=0.5)
            gnt_machine.barh(op.source.machine.id, op.source.duration, left=op.start_time, height=0.5)
            
        # reset x-limit
        for axis in axes:
            axis.relim()
            axis.autoscale()


    def __create_job_chain(self):
        '''Initialize job chain based on the sequence of operations.'''
        # group operations with job
        job_chains = defaultdict(list)
        for op in self.__ops:
            job_chains[op.source.job].append(op)
        
        # create chain for operations of each job
        def create_chain(ops:list):
            pre = None
            for op in ops:
                op.pre_job_op = pre
                pre = op
        for job, ops in job_chains.items():
            create_chain(ops)

 
    def __update_graph(self):
        '''Update the associated directed graph and the topological order accordingly.'''
        # add the dummy source and sink node
        source, sink = OperationStep(), OperationStep()

        # identical directed graph
        graph = DirectedGraph()
        for op in self.__ops:
            # job chain edge
            if op.pre_job_op is None:
                graph.add_edge(source, op)
            
            if op.next_job_op:
                graph.add_edge(op, op.next_job_op)
            else:
                graph.add_edge(op, sink)
            
            # machine chain edge
            if op.next_machine_op and op.next_machine_op!=op.next_job_op:
                graph.add_edge(op, op.next_machine_op)

        # topological order:
        # except the dummy source and sink nodes
        ops = graph.sort()
        self.__sorted_ops = ops[1:-1] if ops else None


        