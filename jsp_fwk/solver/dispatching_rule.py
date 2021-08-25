'''
The sequence of jobs/operations is determined by DISPATCHING RULE:
When a machine becomes available, imminent operations waiting in the queue are prioritized 
by using a dispatching rule. Then, the operation with the highest priority is selected and 
scheduled at the machine. 

A dispatching rule might be one of the basic dispatching rules below, or a combination of 
several of them.

Kaban, A. et al. “Comparison of dispatching rules in job-shop scheduling problem using simulation: 
a case study.” International Journal of Simulation Modelling 11 (2012): 129-140.

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
            # sort by priority            
            head_ops.sort(key=lambda op: self.__dispatching_rule(op, solution))

            # dispatch operation with the first priority
            op = head_ops[0]
            solution.dispatch(op)
            
            # next loop
            next_job_op = op.next_job_op
            if next_job_op is None:
                head_ops = head_ops[1:]
            else:
                head_ops[0] = next_job_op


class DisPatchingRules:

    @classmethod
    def get(cls, name:str):
        '''Get rule method by name.'''
        fun_rule = cls.__dict__.get(name, None)
        if not fun_rule:
            raise JSPException('Invalid rule name.')
        return fun_rule.__func__


    @staticmethod
    def SPT(op:OperationStep, solution:JSSolution):
        '''Shortest Processing Time.'''
        return op.source.duration

    @staticmethod
    def LPT(op:OperationStep, solution:JSSolution):
        '''Longest Processing Time.'''
        return -DisPatchingRules.SPT(op, solution)
    

    @staticmethod
    def SPS(op:OperationStep, solution:JSSolution):
        '''Shortest Process Sequence.'''
        job = solution.job_head(op)
        return len(solution.job_ops[job])    

    @staticmethod
    def LPS(op:OperationStep, solution:JSSolution):
        '''Longest Process Sequence.'''
        return -DisPatchingRules.SPS(op, solution)

    
    @staticmethod
    def STPT(op:OperationStep, solution:JSSolution):
        '''Shortest Total Processing Time.'''
        job = solution.job_head(op)
        return sum(op.source.duration for op in solution.job_ops[job])
    
    @staticmethod
    def LTPT(op:OperationStep, solution:JSSolution):
        '''Longest Total Processing Time.'''
        return -DisPatchingRules.STPT(op, solution)
    

    @staticmethod
    def ECT(op:OperationStep, solution:JSSolution):
        '''Earliest Creation Time.'''
        return op.pre_job_op.end_time
    
    @staticmethod
    def LCT(op:OperationStep, solution:JSSolution):
        '''Longest Creation Time.'''
        return -DisPatchingRules.ECT(op, solution)
    

    @staticmethod
    def SWT(op:OperationStep, solution:JSSolution):
        '''Shortest Waiting Time.'''
        arrive_time = op.pre_job_op.end_time
        machine_time = solution.machine_head(op).tailed_machine_op.end_time
        return max(machine_time-arrive_time, 0)
    
    @staticmethod
    def LWT(op:OperationStep, solution:JSSolution):
        '''Longest waiting Time.'''
        return -DisPatchingRules.SWT(op, solution)

    @staticmethod
    def LTWR(op:OperationStep, solution:JSSolution):
        '''Least Total Work Remaining.'''
        num = 0
        ref = op
        while ref:
            num += ref.source.duration
            ref = ref.next_job_op
        return num

    @staticmethod
    def MTWR(op:OperationStep, solution:JSSolution):
        '''Most Total Work Remaining.'''
        return -DisPatchingRules.LTWR(op, solution)


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
        remaining = DisPatchingRules.LTWR(op, solution) - 1.5*op.source.duration
        return DisPatchingRules.EST(op, solution), -remaining
    

    @staticmethod
    def IHH(op:OperationStep, solution:JSSolution):
        '''Improved HH rule.'''
        return DisPatchingRules.EST(op, solution), -DisPatchingRules.LTWR(op, solution)/op.source.duration
    
