'''Variable of Job-Shop problem, connecting Operation instance and associated 
variables to solve, i.e. the sequence of operations assigned in same machine.
'''

from .domain import (Base, Operation)


class JobStep:
    
    def __init__(self) -> None:
        '''An operation step in job chain. '''
        # pre-defined job chain
        self.__pre_job_op = None    # type: JobStep
        self.__next_job_op = None   # type: Operation
    
    @property
    def pre_job_op(self): return self.__pre_job_op

    @property
    def next_job_op(self): return self.__next_job_op

    @pre_job_op.setter
    def pre_job_op(self, op):
        self.__pre_job_op = op
        if op is not None: op.__next_job_op = self

    
class MachineStep:
    
    def __init__(self) -> None:
        '''An operation step in machine chain. '''
        # machine chain to solve
        self.__pre_machine_op = None    # type: MachineStep
        self.__next_machine_op = None   # type: Operation
    
    @property
    def pre_machine_op(self): return self.__pre_machine_op

    @property
    def next_machine_op(self): return self.__next_machine_op

    @pre_machine_op.setter
    def pre_machine_op(self, op):
        self.__pre_machine_op = op
        if op is not None: op.__next_machine_op = self



class OperationStep(Base, JobStep, MachineStep):

    def __init__(self, op:Operation=None) -> None:
        '''An operation step wrapping the source operation instance. A step might belong to
        two kinds of sequence chain: a job chain and a machine chain.

        * A job chain is the sequence of operations to complete a job, which is constant in 
        Job-Shop problem
        * while a machine chain is the sequence of operations assigned to a same machine, 
        which is to be solved.

        Args:
            op (Operation): The source operation.
        '''
        Base.__init__(self, op.id if op else -1)
        JobStep.__init__(self)
        MachineStep.__init__(self)

        # the source operation
        self.__source = op

        # final variable in mathmestical model, while shadow variable in disjunctive graph 
        # model, i.e. the start time is determined by operation sequence
        self.start_time = 0.0
    

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id})'

    @property
    def source(self): return self.__source

    @property
    def end_time(self) -> float: return self.start_time + self.__source.duration


    def update_start_time(self):
        '''Update start time: the late start time in job chain and machine chain.
        NOTE: this method is available for disjunctive graph model only.
        '''
        self.start_time = max(self.__job_chain_start_time(), self.__machine_chain_start_time())
    

    def copy(self):
        '''Copy to a new instance with same properties. Keep same job chain sequence.'''
        op = OperationStep(self.__source)
        op.__pre_job_op = self.__pre_job_op
        if self.__next_job_op:
            self.__next_job_op.pre_job_op = op
        return op

    
    def __job_chain_start_time(self) -> float:
        '''The earlist start time in job chain. It's right after the end time of previous operation;
        or start immediately if this is the first operation.'''
        return 0.0 if self.pre_job_op is None else self.pre_job_op.end_time
    

    def __machine_chain_start_time(self):
        '''The earlist start time in machine chain. It's right after the end time of previous operation;
        or start immediately if this is the first operation.
        '''
        return 0.0 if self.pre_machine_op is None else self.pre_machine_op.end_time