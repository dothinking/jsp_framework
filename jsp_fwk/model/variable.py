'''Variable of Job-Shop problem, connecting Operation instance and associated 
variables to solve, i.e. the sequence of operations assigned in same machine.
'''

from .domain import (Base, Operation)


class Step(Base):
    
    def __init__(self, source:Base=None) -> None:
        '''A wrapper of domain instance.

        Args:
            source (Base): The domain instance, e.g. Job, Machine or Operation.
        '''        
        super().__init__(source.id if source else -1)

        # the source object
        self.__source = source    

    @property
    def source(self): return self.__source

    @property
    def end_time(self) -> float:
        '''The time when a step is completed. For the first job step or machine step, 
        it's 0 by default, i.e. start immediately.
        '''
        return 0.0


class JobStep(Step):
    
    def __init__(self, source:Base=None) -> None:
        '''An operation step in job chain. 
        
        NOTE: the job itself is wrapped as a JobStep and is the first step in job chain.
        '''
        super().__init__(source=source)
        # pre-defined job chain
        self.__pre_job_op = None    # type: JobStep
        self.__next_job_op = None   # type: OperationStep
    
    @property
    def pre_job_op(self): return self.__pre_job_op

    @property
    def next_job_op(self): return self.__next_job_op

    @pre_job_op.setter
    def pre_job_op(self, op):
        self.__pre_job_op = op
        if hasattr(op, 'next_job_op'): op.__next_job_op = self

    
class MachineStep(Step):
    
    def __init__(self, source:Base=None) -> None:
        '''An operation step in machine chain.
        
        NOTE: the machine itself is wrapped as a MachineStep and is the first step 
        in machine chain.
        '''
        super().__init__(source=source)
        # machine chain to solve
        self.__pre_machine_op = None    # type: MachineStep
        self.__next_machine_op = None   # type: OperationStep
    
    @property
    def pre_machine_op(self): return self.__pre_machine_op

    @property
    def next_machine_op(self): return self.__next_machine_op

    @pre_machine_op.setter
    def pre_machine_op(self, op):
        self.__pre_machine_op = op
        if hasattr(op, 'next_machine_op'): op.__next_machine_op = self
    
    @property
    def tailed_machine_op(self):
        '''The last step in current machine chain.'''
        step = self
        while True:
            if step.__next_machine_op is None: return step
            step = step.__next_machine_op
    
    @property
    def utilization(self):
        '''Utilization of current machine: service_time / (service_time + free_time).'''
        service_time, total_time = 0, 0
        op = self.__next_machine_op
        while op:
            service_time += op.source.duration
            total_time = op.end_time
            op = op.__next_machine_op
        
        return service_time/total_time if total_time else 1.0


class OperationStep(JobStep, MachineStep):

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
        JobStep.__init__(self, op)
        MachineStep.__init__(self, op)

        # final variable in mathmestical model, while shadow variable in disjunctive graph 
        # model, i.e. the start time is determined by operation sequence
        self.__start_time = 0.0
    

    @property
    def start_time(self) -> float: return self.__start_time

    @property
    def end_time(self) -> float: return self.__start_time + self.source.duration


    def update_start_time(self, start_time:float=None):
        '''Set start time directly, or update start time based on operations sequence in disjunctive 
        graph model. Note the difference to `estimated_start_time`, which is to estimate start time
        before dispatching to the machine, while this method is run after dispatched to a machine. 
        
        Args:
            start_time (float): The tartget time. Default to None, update start time based on sequence.
        '''
        if start_time is not None:
            self.__start_time = start_time

        # if dispatched, dertermine start time by the previous operations in both job chain and 
        # machine chain. Otherwise, use the default start time
        elif self.pre_machine_op:        
            self.__start_time = max(self.pre_job_op.end_time, self.pre_machine_op.end_time)