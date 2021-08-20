'''
The sequence of jobs/operations is determined by DISPATCHING RULE:
When a machine becomes available, imminent operations waiting in the queue are prioritized 
by using a dispatching rule. Then, the operation with the highest priority is selected and 
scheduled at the machine. 

A dispatching rule might be one of the basic dispatching rules below, or a combination of 
several of them.

- Shortest Processing Time (SPT): Prefer the operation with the shortest processing time.
- Longest Processing Time (LPT): Prefer the operation with the longest processing time.
- Shortest Job First (SJF): Prefer the operation of which the job possesses the shortest 
  total processing time.
- Longest Job First (LJF): Prefer the operation of which the job possesses the longest 
  total processing time.
- Least Work Remaining (LWKR): Prefer the operation for which the sum of the operation 
  length and successor operations' lengths is the least.
- Most Work Remaining (MWKR): Prefer the operation for which the sum of the operation 
  length and successor operations' lengths is the most.
- Most Operations Remaining (MOPR): the preferred operation of part with the largest number 
  still unrealized operations.
- Relative Least Work Remaining (RLWKR): As LWKR but normalized by total job length.
- Relative Most Work Remaining (RMWKR): As MWKR but normalized by total job length.
- Shortest Waiting Time (SWT): Prefer the operation that was enqueued as the last.
- Longest Waiting Time (LWT): Prefer the operation that was enqueued as the first.
- Urgency Next (UN): Prefer the operation of which the successor operation's machine becomes 
  idle as the first (based on the current queues).
- Urgency Any (UA): Prefer the operation of which one of the successor operation's machine 
  becomes idle as the first (based on the current queues).
- First In First Out (FIFO): The job which arrives first enters service first.
- Last Come First Served (LCFS): Jobs are processed in the order of last to first in which they 
arrive at the machine.

Study [DOI: 10.5281/zenodo.1422477] shows that:

Shortest Processing Time (SPT) is the efficient method when the number of machines is 2 and number 
of jobs are (10, 30, and 100), Most Operations Remaining (MOPR) is the efficient method when the 
number of machines is 10 and number of jobs are (10, 30, and 100) and Most Work Remaining (MWKR) is 
the efficient method when the number of machines is 20 and number of jobs are (10, 30, and 100).
'''

from ..common.exception import JSPException
from ..model.variable import OperationStep
from ..model.solver import JSSolver
from ..model.problem import JSProblem
from ..model.solution import JSSolution



class PriorityDispatchSolver(JSSolver):
    '''General Priority Dispatching Solver.'''
    
    def __init__(self, rule:str=None, fun_rule=None) -> None:
        '''Dispatching operation with priority defined by pre-defined or user rule.

        Args:
            rule (str, optional): Pre-defined rule name. Defaults to None.
            fun_rule (function, optional): User defined function for dispatching rule. It takes
            an OperationStep instance as input, and returns a tuple representing the priority. 
            The lower value, the higher priority.

            ```python
            def fun_rule(op:OperationStep) -> tuple
            ```
        '''        
        super().__init__()

        if rule:
            self.__dispatching_rule = DisPatchingRules.get(rule.upper())
        elif fun_rule:
            self.__dispatching_rule = fun_rule
        else:
            raise JSPException('Invalid rule.')
    

    def do_solve(self, problem: JSProblem):
        solution = JSSolution(problem=problem)

        # collect imminent operations in the processing queue
        head_ops = [job_step.next_job_op for job_step in solution.job_ops]

        # dispatch operation by priority
        i = 1
        while head_ops:
            # sort by priority            
            head_ops.sort(key=self.__dispatching_rule)

            # dispatch operation with the first priority
            op = head_ops[0]
            pre_machine_op = solution.machine_head(op).tailed_machine_op
            op.pre_machine_op = pre_machine_op
            solution.evaluate() # update start time accordingly

            # update gantt chart
            if i % 20 == 0: 
                problem.update_solution(solution=solution)
            
            # next loop
            i += 1
            next_job_op = op.next_job_op
            if next_job_op is None:
                head_ops = head_ops[1:]
            else:
                head_ops[0] = next_job_op
        
        # final result
        solution.evaluate()
        problem.update_solution(solution=solution)
    


class PriorityDispatchProSolver(PriorityDispatchSolver):
    '''Improved version of Priority Dispatching Solver with one step estimation.'''

    def do_solve(self, problem: JSProblem):
        pass



class DisPatchingRules:

    @classmethod
    def get(cls, name:str='t'):
        '''Get rule method by name.'''
        fun_rule = cls.__dict__.get(name, None)
        if not fun_rule:
            raise JSPException('Invalid rule name.')
        return fun_rule.__func__

    @staticmethod
    def SPT(op:OperationStep):
        '''Dispatching rules: Shortest Processing Time.'''
        return op.source.duration


    @staticmethod
    def MOPR(op:OperationStep):
        '''Dispatching rule: Most Operations Remaining.'''
        num = 0
        next_job_op = op.next_job_op
        while next_job_op:
            num += 1
            next_job_op = next_job_op.next_job_op
        return -num


    @staticmethod
    def MWKR(op:OperationStep):
        '''Dispatching rule: Most Work Remaining.'''
        num = 0
        ref = op
        while ref:
            num += ref.source.duration
            ref = ref.next_job_op
        return -num


    @staticmethod
    def T(op:OperationStep):
        '''Dispatching rule: 黄志. 作业车间调度问题的一种启发式算法.'''
        remaining = -DisPatchingRules.MWKR(op) - 1.5*op.source.duration
        return op.estimated_start_time, -remaining