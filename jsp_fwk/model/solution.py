'''Solution of Job-Shop Schedule Problem, especially the sequence of operations
assigned in each machine, and the deduced start time of each operation accordingly.
'''

from collections import defaultdict
from matplotlib.container import BarContainer
from .domain import (Operation,Cloneable)
from .variable import (JobStep, MachineStep, OperationStep)
from ..common.graph import DirectedGraph
from .problem import JSProblem


class JSSolution(Cloneable):

    def __init__(self, problem:JSProblem) -> None:
        '''Initialize solution by copying all operations from `problem`.

        Args:
            problem (JSProblem): Problem to solve.
        '''
        self.__ops = [OperationStep(op) for op in problem.ops]

        # group operation steps with job and machine and initialize job chain
        self.__job_ops = defaultdict(list)
        self.__machine_ops = defaultdict(list)
        self.__create_job_chain()

        # operations in topological order: available for disjunctive graph model only
        self.__sorted_ops = None # type: list[OperationStep]
    

    @property
    def ops(self) -> list: 
        '''All operation steps in job related order: 
        [job0_op0, job0_op1, ..., job1_op0, job1_op1, ...]'''
        return self.__ops

    @property
    def job_ops(self): 
        '''Operation steps grouped by job: {job_step: [op0, op1, op2, ...]}.'''
        return self.__job_ops

    @property
    def machine_ops(self): 
        '''Operation steps grouped by machine: {machine_step: [op0, op5, op8, ...]}.'''
        return self.__machine_ops

    @property
    def sorted_ops(self): 
        '''Topological order of the operation steps. Only available for disjunctive graph model.'''
        return self.__sorted_ops

    @property
    def makespan(self) -> float:
        '''Makespan of current solution. 
        Only available when the solution is feasible; otherwise None.
        '''
        return max(map(lambda op: op.end_time, self.__ops))
    

    def find(self, source_op:Operation):
        '''Find the associated step with source operation.'''
        for op in self.__ops:
            if op.source==source_op:
                return op
        return None
        

    def job_head(self, op:OperationStep):
        '''The first step in job chain of specified `op`, i.e. the virtual job step.'''
        for job_step in self.__job_ops:
            if job_step.source==op.source.job:
                return job_step
        return None
    

    def machine_head(self, op:OperationStep):
        '''The first step in machine chain of specified `op`, i.e. the virtual machine step.'''
        for machine_step in self.__machine_ops:
            if machine_step.source==op.source.machine:
                return machine_step
        return None

    @property
    def imminent_ops(self):
        '''Collect imminent operations in the processing queue.'''
        head_ops = []
        for job_step in self.__job_ops:
            op = job_step.next_job_op
            while op and op.pre_machine_op:
                op = op.next_job_op
            if op: head_ops.append(op)
        return head_ops

    
    def copy(self):
        '''Hard copy of current solution. Override `Cloneable.copy()`.'''
        # copy step instances and job chain
        ops = [op.source for op in self.__ops]
        solution = JSSolution(problem=JSProblem(ops=ops))

        # copy machine chain
        def map_source_to_step(solution):
            '''map source instance to step instance'''
            step_map = {}
            for machine_step, ops in solution.machine_ops.items():
                step_map[machine_step.source] = machine_step
                for op_step in ops:
                    step_map[op_step.source] = op_step
            return step_map
        step_map = map_source_to_step(solution)

        for op, new_op in zip(self.__ops, solution.ops):
            if not op.pre_machine_op: continue
            new_op.pre_machine_op = step_map[op.pre_machine_op.source]
        
        # update
        solution.evaluate()

        return solution


    def estimated_start_time(self, op:OperationStep) -> float:
        '''Estimate the start time if it's dispatched to the end of current machine chain.'''
        machine_op = self.machine_head(op).tailed_machine_op
        return max(op.pre_job_op.end_time, machine_op.end_time)


    def dispatch(self, op:OperationStep):
        '''Dispatch the operation step to the associated machine.'''
        pre_machine_op = self.machine_head(op).tailed_machine_op
        op.pre_machine_op = pre_machine_op
        self.evaluate(op=op) # update start time accordingly


    def is_feasible(self) -> bool:
        '''If current solution is valid or not. 
        Note to call this method after evaluating the solution if based on disjunctive graph model.
        '''
        # check topological order if disjunctive graph model, 
        # otherwise check the start time further directly
        if self.__sorted_ops: return True

        # validate job chain        
        for job, ops in self.__job_ops.items():
            ops.sort(key=lambda op: op.id) # sort in job sequence, i.e. default id order
            ref = 0
            for op in ops:
                if op.end_time <= ref: return False
                ref = op.end_time
        
        # validate machine chain        
        for machine, ops in self.__machine_ops.items():
            ops.sort(key=lambda op: op.start_time) # sort by start time
            ref = 0
            for op in ops:
                if op.end_time <= ref: return False
                ref = op.end_time
        
        return True


    def evaluate(self, op:OperationStep=None) -> bool:
        '''Evaluate specified and succeeding operations of current solution, especially 
        work time. Generally the machine chain was changed before calling this method.

        NOTE: this method is only available for disjunctive graph model.

        Args:
            op (OperationStep, optional): The operation step to update. Defaults to None,
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
        for op in self.__sorted_ops[pos:]:
            op.update_start_time()
        
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
        # group operations with job and machine, respectively
        job_ops = defaultdict(list)
        machine_ops = defaultdict(list)
        for op in self.__ops:
            job_ops[op.source.job].append(op)
            machine_ops[op.source.machine].append(op)
        
        # convert the key form Job/Machine to JobStep/MachineStep
        self.__job_ops = { JobStep(job) : ops for job, ops in job_ops.items() }
        self.__machine_ops = { MachineStep(machine) : ops for machine, ops in machine_ops.items() }
        
        # create chain for operations of each job
        def create_chain(job_step:JobStep, ops:list):
            pre = job_step
            for op in ops:
                op.pre_job_op = pre
                pre = op

        for job, ops in self.__job_ops.items(): create_chain(job, ops)    


    def __update_graph(self):
        '''Update the associated directed graph and the topological order accordingly.'''
        # add the dummy source and sink node
        source, sink = OperationStep(), OperationStep()

        # identical directed graph
        graph = DirectedGraph()
        for op in self.__ops:
            # job chain edge
            if not isinstance(op.pre_job_op, OperationStep): # first real operation step
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


        
