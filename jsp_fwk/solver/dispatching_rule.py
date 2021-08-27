'''
The sequence of jobs/operations is determined by DISPATCHING RULE:
When a machine becomes available, imminent operations waiting in the queue are prioritized 
by using a dispatching rule. Then, the operation with the highest priority is selected and 
scheduled at the machine. 

A dispatching rule might be one of the basic dispatching rules below, or a combination of 
several of them.

Kaban, A. et al. "Comparison of dispatching rules in job-shop scheduling problem using simulation: 
a case study." International Journal of Simulation Modelling 11 (2012): 129-140.

No. Rules   Description                     Type 
----------------------------------------------------
1   FIFO    First In First Out              Static 
2   LIFO    Last In First Out               Static 
3   SPT     Shortest Processing Time        Static 
4   LPT     Longest Processing Time         Static 
5   SPS     Shortest Process Sequence       Static 
6   LPS     Longest Process Sequence        Static 
7   STPT    Shortest Total Processing Time  Static 
8   LTPT    Longest Total Processing Time   Static 
9   ECT     Earliest Creation Time          Dynamic 
10  LCT     Longest Creation Time           Dynamic 
11  SWT     Shortest Waiting Time           Dynamic 
12  LWT     Longest Waiting Time            Dynamic 
13  LTWR    Least Total Work Remaining      Dynamic 
14  MTWR    Most Total Work Remaining       Dynamic 

These rules are based on 3 static parameters:

- Processing Time       : Time required to complete an operation on a specific machine. 
- Process Sequence      : Total count of operations to complete a job. 
- Total Processing Time : Total time required to complete a job. 

and 3 dynamic parameters depending on the passage of time: 

- Creation Time         : The time when an operation arriving at a machine. 
- Waiting Time          : The time that an operation spent when waiting in the queue line on machine. 
- Total Work Remaining  : The time for a job to complete the remaining operations. 
'''

from ..common.exception import JSPException
from ..model.variable import OperationStep
from ..model.solver import JSSolver
from ..model.problem import JSProblem
from ..model.solution import JSSolution



class PriorityDispatchSolver(JSSolver):
    '''General Priority Dispatching Solver.'''
    
    def __init__(self, name:str=None, rule:str=None, fun_rule=None) -> None:
        '''Dispatching operation with priority defined by pre-defined or user rule.

        Args:
            name (str, optional): Solver name.
            rule (str, optional): Pre-defined rule name. Defaults to None.
            fun_rule (function, optional): User defined function for dispatching rule. It takes
            an OperationStep instance and associated JSSolution instance as inputs, and returns 
            a tuple representing the priority. The lower value, the higher priority.

            ```python
            def fun_rule(op:OperationStep, solution:JSSolution) -> tuple
            ```
        '''        
        super().__init__(name)

        if rule:
            self.__dispatching_rule = DisPatchingRules.get(rule.upper())
        elif fun_rule:
            self.__dispatching_rule = fun_rule
        else:
            raise JSPException('Invalid rule.')
    

    def do_solve(self, problem: JSProblem):
        solution = JSSolution(problem=problem)
        self.solving_iteration(solution=solution)
        problem.update_solution(solution=solution)
    

    def solving_iteration(self, solution:JSSolution):
        '''One iteration applying priority dispatching rule.'''
        # move form
        # collect imminent operations in the processing queue
        head_ops = solution.imminent_ops

        # dispatch operation by priority
        while head_ops:
            # dispatch operation with the first priority
            op = min(head_ops, key=lambda op: self.__dispatching_rule(op, solution))
            solution.dispatch(op)
            
            # update imminent operations
            pos = head_ops.index(op)
            next_job_op = op.next_job_op
            if next_job_op is None:
                head_ops = head_ops[0:pos] + head_ops[pos+1:]
            else:
                head_ops[pos] = next_job_op


class DisPatchingRules:

    @classmethod
    def get(cls, name:str):
        '''Get rule method by name.'''
        fun_rule = cls.__dict__.get(name, None)
        if not fun_rule:
            raise JSPException('Invalid rule name.')
        return fun_rule.__func__

    # static parameters:
    # - Processing Time       : Time required to complete an operation on a specific machine. 
    # - Process Sequence      : Total count of operations to complete a job. 
    # - Total Processing Time : Total time required to complete a job. 
    @staticmethod
    def PT(op:OperationStep, solution:JSSolution):
        '''Processing Time.'''
        return op.source.duration

    @staticmethod
    def PS(op:OperationStep, solution:JSSolution):
        '''Process Sequence.'''
        job = solution.job_head(op)
        return len(solution.job_ops[job])   

    @staticmethod
    def TPT(op:OperationStep, solution:JSSolution):
        '''Total Processing Time.'''
        job = solution.job_head(op)
        return sum(op.source.duration for op in solution.job_ops[job]) 
    

    # dynamic parameters: 
    # - Creation Time         : The time when an operation arriving at a machine. 
    # - Waiting Time          : The time that an operation spent when waiting in the queue line on machine. 
    # - Total Work Remaining  : The time for a job to complete the remaining operations. 
    @staticmethod
    def CT(op:OperationStep, solution:JSSolution):
        '''Creation Time.'''
        return op.pre_job_op.end_time

    @staticmethod
    def WT(op:OperationStep, solution:JSSolution):
        '''Waiting Time.'''
        arrive_time = op.pre_job_op.end_time
        machine_time = solution.machine_head(op).tailed_machine_op.end_time
        return max(machine_time-arrive_time, 0)
    
    @staticmethod
    def TWR(op:OperationStep, solution:JSSolution):
        '''Total Work Remaining.'''
        num = 0
        ref = op
        while ref:
            num += ref.source.duration
            ref = ref.next_job_op
        return num

    # ------------------------------
    # static rules
    # ------------------------------
    @staticmethod
    def SPT(op:OperationStep, solution:JSSolution):
        '''Shortest Processing Time.'''
        return DisPatchingRules.PT(op, solution)

    @staticmethod
    def LPT(op:OperationStep, solution:JSSolution):
        '''Longest Processing Time.'''
        return -DisPatchingRules.PT(op, solution)
    
    @staticmethod
    def SPS(op:OperationStep, solution:JSSolution):
        '''Shortest Process Sequence.'''
        return DisPatchingRules.PS(op, solution)

    @staticmethod
    def LPS(op:OperationStep, solution:JSSolution):
        '''Longest Process Sequence.'''
        return -DisPatchingRules.PS(op, solution)
    
    @staticmethod
    def STPT(op:OperationStep, solution:JSSolution):
        '''Shortest Total Processing Time.'''
        return DisPatchingRules.TPT(op, solution)
    
    @staticmethod
    def LTPT(op:OperationStep, solution:JSSolution):
        '''Longest Total Processing Time.'''
        return -DisPatchingRules.TPT(op, solution)
    

    # ------------------------------
    # dynamic rules
    # ------------------------------
    @staticmethod
    def ECT(op:OperationStep, solution:JSSolution):
        '''Earliest Creation Time.'''
        return DisPatchingRules.CT(op, solution)
    
    @staticmethod
    def LCT(op:OperationStep, solution:JSSolution):
        '''Longest Creation Time.'''
        return -DisPatchingRules.CT(op, solution)
    

    @staticmethod
    def SWT(op:OperationStep, solution:JSSolution):
        '''Shortest Waiting Time.'''
        return DisPatchingRules.WT(op, solution)
    
    @staticmethod
    def LWT(op:OperationStep, solution:JSSolution):
        '''Longest waiting Time.'''
        return -DisPatchingRules.WT(op, solution)

    @staticmethod
    def LTWR(op:OperationStep, solution:JSSolution):
        '''Least Total Work Remaining.'''
        return DisPatchingRules.TWR(op, solution)

    @staticmethod
    def MTWR(op:OperationStep, solution:JSSolution):
        '''Most Total Work Remaining.'''
        return -DisPatchingRules.TWR(op, solution)


    @staticmethod
    def EST(op:OperationStep, solution:JSSolution):
        '''Earliest Start Time.'''
        return solution.estimated_start_time(op)
    
    @staticmethod
    def LST(op:OperationStep, solution:JSSolution):
        '''Longest Start Time.'''
        return -DisPatchingRules.EST(op, solution)


    @staticmethod
    def HH(op:OperationStep, solution:JSSolution):
        '''黄志, 黄文奇. 作业车间调度问题的一种启发式算法.'''
        remaining = DisPatchingRules.TWR(op, solution) - 1.5*op.source.duration
        return DisPatchingRules.EST(op, solution), -remaining
    

    @staticmethod
    def IHH(op:OperationStep, solution:JSSolution):
        '''Improved HH rule.'''
        return DisPatchingRules.EST(op, solution), -DisPatchingRules.TWR(op, solution)/op.source.duration