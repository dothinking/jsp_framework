'''Solution of Job-Shop Schedule Problem.
The variable is start time of each operation, which can be solved directly, or solve
machine chain operations sequence first and deduce start time accordingly.
'''
from typing import (List, Union)
from collections import defaultdict
from .domain import (Clone, Job, Machine, Operation)
from .variable import OperationStep
from ..common.graph import DirectedGraph
from ..common.plot import (plot_gantt_chart_axes, plot_gantt_chart_bars, plot_disjunctive_graph)
from .problem import JSProblem


class JSSolution(Clone):
    '''Solution of job-shop problem.'''

    def __init__(self, problem:JSProblem, direct_mode:bool=True) -> None:
        '''Initialize solution by copying all operations from `problem`.

        Args:
            problem (JSProblem): Problem to solve.
            direct_mode (bool): solve operation start time directly if True, otherwise,
                solve machine chain first and deduce start time accordingly.
        '''
        self.__direct_mode = direct_mode
        self.__ops = [OperationStep(op) for op in problem.ops]

        # group operation steps with job and machine and initialize job chain
        self.__job_ops = None
        self.__machine_ops = None
        self.__create_job_chain()

    @property
    def direct_mode(self):
        '''Solve start time directly or solve machine chain sequence first.'''
        return self.__direct_mode

    @property
    def ops(self) -> List[OperationStep]:
        '''All operation steps in job related order:
        [j0_m1_op0, j0_m2_op1, ..., j1_m2_op0, j1_m1_op1, ...]'''
        return self.__ops

    @property
    def job_ops(self) -> List[OperationStep]:
        '''Virtual job steps.'''
        return self.__job_ops

    @property
    def machine_ops(self) -> List[OperationStep]:
        '''Virtual machine steps.'''
        return self.__machine_ops

    @property
    def makespan(self) -> float:
        '''Makespan of current solution.
        Only available when the solution is feasible; otherwise None.
        '''
        return max(map(lambda op: op.end_time, self.ops))


    def job_head(self, op:OperationStep) -> OperationStep:
        '''The virtual job step that current operation belonging to.
        Note the difference to `op.top_job_op`.
        '''
        return self.find(op.source.job)

    def machine_head(self, op:OperationStep) -> OperationStep:
        '''The virtual machine step that current operation will be dispatched to.
        Note the difference to `op.top_machine_op`.'''
        return self.find(op.source.machine)


    def find(self, source_op:Operation):
        '''Find the associated step with source operation.'''
        def _find(ops:List[OperationStep], source:Operation):
            for op in ops:
                if op.source==source: return op
            return None
        if isinstance(source_op, Machine): return _find(self.machine_ops, source_op)
        if isinstance(source_op, Job): return _find(self.job_ops, source_op)
        return _find(self.ops, source_op)


    def dispatch(self, op:Union[OperationStep, List[OperationStep]], update_time:bool=True):
        '''Dispatch the operation step/steps to the associated machine.'''
        def _dispatch(op:OperationStep):
            top = self.find(op.source.machine)
            top.tail_machine_op.connect_machine_op(op)

        # dispatch operation in specified sequence
        ops = [op] if isinstance(op, OperationStep) else op
        for s in ops: _dispatch(s)

        # update start time
        if update_time: self.update_start_time(op=ops[0])


    @property
    def imminent_ops(self):
        '''Collect imminent operations in the processing queue.'''
        head_ops = []
        for job_step in self.job_ops:
            op = job_step.next_job_op
            while op and op.pre_machine_op: # dispatched
                op = op.next_job_op
            if op: head_ops.append(op)
        return head_ops


    def copy(self):
        '''Hard copy of current solution. Override `Clone.copy()`.'''
        # copy step instances and job chain
        ops = [op.source for op in self.ops]
        solution = JSSolution(problem=JSProblem(ops=ops))

        # copy machine chain
        step_map = {op.source:op for op in solution.ops + solution.machine_ops}
        for op, new_op in zip(self.ops, solution.ops):
            if not op.pre_machine_op: continue
            step_map[op.pre_machine_op.source].connect_machine_op(new_op)

        # update
        solution.update_start_time()
        return solution


    @property
    def is_feasible(self) -> bool:
        '''If current solution is valid or not.
        Note to call this method after evaluating the solution if based on disjunctive graph model.
        '''
        # update start time first if not direct mode
        if not self.direct_mode: self.update_start_time()

        # validate job chain
        for job in self.job_ops:
            ref  = 0.0
            op = job.next_job_op
            while op:
                if op.start_time < ref: return False
                ref = op.end_time
                op = op.next_job_op

        # validate machine chain
        machine_ops = defaultdict(list)
        for op in self.ops:
            machine_ops[op.source.machine].append(op)

        for ops in machine_ops.values():
            ops.sort(key=lambda op: op.start_time) # sort by start time
            ref = 0
            for op in ops:
                if op.start_time < ref: return False
                ref = op.end_time
        return True


    def update_start_time(self, op:OperationStep=None) -> bool:
        '''Evaluate specified and succeeding operations of current solution, especially
        work time. Generally the machine chain was changed before calling this method.

        NOTE: this method is only available for disjunctive graph model.

        Args:
            op (OperationStep, optional): The operation step to update. Defaults to None,
                i.e., the first operation.

        Returns:
            bool: True if current solution is feasible.
        '''
        # update topological order due to the changed machine chain
        sorted_ops = self.topological_sort
        if not sorted_ops: return False

        # the position of target process
        pos = 0 if op is None else sorted_ops.index(op)

        # update process by the topological order
        for s in sorted_ops[pos:]: s.update_start_time()
        return True


    @property
    def topological_sort(self) -> List[OperationStep]:
        '''Topological order based on directed graph of current solution.'''
        # add the dummy source and sink node
        source, sink = OperationStep(), OperationStep()

        # identical directed graph
        graph = DirectedGraph()
        for op in self.ops:
            # job chain edge
            if isinstance(op.pre_job_op.source, Job): # top of job chain
                graph.add_edge(source, op)
            if op.next_job_op:
                graph.add_edge(op, op.next_job_op)
            else:
                graph.add_edge(op, sink)

            # machine chain edge
            if op.next_machine_op and op.next_machine_op!=op.next_job_op:
                graph.add_edge(op, op.next_machine_op)

        # topological order
        ops = graph.sort()
        return ops[1:-1] if ops else None # except the dummy nodes


    def plot_gantt_chart(self):
        '''Plot gantt chart.'''
        from matplotlib import pyplot as plt

        _, axis_job, axis_machine = plot_gantt_chart_axes(
            jobs=[op.source for op in self.job_ops],
            machines=[op.source for op in self.machine_ops]
        )
        plot_gantt_chart_bars(axis_job, axis_machine, self.ops, self.makespan)
        plt.show()


    def plot_disjunctive_graph(self):
        '''Plot disjunctive graph.'''
        def node_id(op): return (op.source.job.id,op.source.machine.id)

        # adaptive size based on machine and job numbers
        m, n = len(self.job_ops), len(self.machine_ops)

        # source and sink nodes
        source, sink = 'S', 'E'

        # node position
        k_w, k_h = 2.0, 1.2 # scale factor
        pos = {
            source: (0, (m-1)/2*k_h),
            sink: (k_w*(n+1), (m-1)/2*k_h)
        }

        # edges in job chain
        job_ops = defaultdict(list)
        for op in self.ops: job_ops[op.source.job].append(op)
        job_edges = []
        for i,job in enumerate(job_ops):
            pre = source
            for j,op in enumerate(job_ops[job], start=1):
                nid = node_id(op)
                pos[nid] = (k_w*j, k_h*i)
                if j==1:
                    job_edges.append((pre, nid, 0))
                else:
                    job_edges.append((node_id(pre), nid, pre.source.duration))
                pre = op
            job_edges.append((node_id(op), sink, op.source.duration))

        # edges in machine chain
        machine_ops = defaultdict(list)
        for op in self.ops:
            machine_ops[op.source.machine].append(op)

        machine_edges = []
        for ops in machine_ops.values():
            ops.sort(key=lambda op: op.start_time) # sort by start time
            pre = ops[0]
            for op in ops[1:]:
                machine_edges.append((node_id(pre), node_id(op)))
                pre = op
        # plot
        plot_disjunctive_graph(num_jobs=m, num_machines=n, pos=pos,
                               job_edges=job_edges, machine_edges=machine_edges)


    def __create_job_chain(self):
        '''Initialize job chain based on the sequence of operations.'''
        # group operations with job and machine, respectively
        job_ops = defaultdict(list)
        machine_ops = defaultdict(list)
        for op in self.ops:
            job_ops[op.source.job].append(op)
            machine_ops[op.source.machine].append(op)

        self.__job_ops = [OperationStep(op) for op in job_ops]
        self.__machine_ops = [OperationStep(op) for op in machine_ops]

        # create chain for operations of each job
        def create_chain(job:OperationStep, ops:List[OperationStep]):
            pre = job
            for op in ops:
                pre.connect_job_op(op)
                pre = op
        for job in self.job_ops:
            create_chain(job, job_ops.get(job.source, []))
