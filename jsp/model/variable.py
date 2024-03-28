'''
Variable of Job-Shop problem, connecting Operation instance and associated
variables to solve, i.e., the sequence of operations assigned to same machine.

Two kinds of sequence chain:
* Job chain is the sequence of operations to complete a job, which is constant in
Job-Shop problem.
* Machine chain is the sequence of operations assigned to same machine, which is
to be solved.

Note the first step of job/machine chain is always a virtual step representing the
job/machine.

+---------+     +-----+     +-----+
| JobStep | --> | OP1 | --> | OP2 | --> ...
+---------+     +-----+     +-----+
'''

from jsp_fwk.common.exception import JSPException
from .domain import (Machine, Operation)


class OperationStep:
    '''Operation step.'''

    def __init__(self, op:Operation=None) -> None:
        '''An operation step wrapping the source operation instance. A step might belong to
        two kinds of sequence chain: a job chain and a machine chain.

        Args:
            op (Operation): The source operation. Note that it might be a virtual step, e.g.,
                machine/job step.
        '''
        self.__source = op # the source object

        # pre-defined job chain
        self.pre_job_op = None    # type: OperationStep
        self.next_job_op = None   # type: OperationStep

        # disjunctive graph model: machine chain to solve
        self.pre_machine_op = None    # type: OperationStep
        self.next_machine_op = None   # type: OperationStep

        # final variable in mathematical model, while shadow variable in disjunctive graph
        # model, i.e., the start time is determined by operation sequence
        self.__start_time = 0.0

    def __repr__(self) -> str:
        job_id = self.source.job.id if self.source.job else None
        machine_id = self.source.machine.id if self.source.machine else None
        return f'{self.__class__.__name__}({job_id}, {machine_id})'

    @property
    def source(self):
        '''Source instance.'''
        return self.__source

    @property
    def start_time(self) -> float:
        '''Starting time of an operation.'''
        return self.__start_time

    @property
    def end_time(self) -> float:
        '''The time when a step is completed.'''
        return self.__start_time + self.source.duration

    def update_start_time(self, start_time:float=None):
        '''Set start time directly, or update start time based on operations sequence in disjunctive
        graph model.

        Args:
            start_time (float): Target time. Default to None, update start time based on sequence.
        '''
        # if dispatched, determine start time by the previous operations in both job chain and
        # machine chain. Otherwise, use the default start time
        if start_time is not None:
            self.__start_time = start_time
        elif self.pre_machine_op:
            self.__start_time = max(self.pre_job_op.end_time, self.pre_machine_op.end_time)


    def dispatch(self, machine_step:"OperationStep"):
        '''Dispatch current step to the specified machine chain.

        Args:
            machine_step (OperationStep): top step of a machine chain.
        '''
        machine_step.tail_machine_op.connect_machine_op(self)


    def connect_job_op(self, op:"OperationStep"):
        '''Create a connect in job chain: self -> op.'''
        if self.source.job != op.source.job:
            raise JSPException(f"Can't connect {self} and {op} due to different Job ID.")

        # break existing links
        next_op = self.next_job_op
        if next_op: next_op.pre_job_op = None
        pre_op = op.pre_job_op
        if pre_op: pre_op.next_job_op = None

        # create new link
        self.next_job_op = op
        op.pre_job_op = self

    def connect_machine_op(self, op:"OperationStep"):
        '''Create a connect in machine chain: self -> op.'''
        if self==op: return
        if self.source.machine!=op.source.machine:
            raise JSPException(f"Can't connect {self} and {op} due to different Machine ID.")

        # break existing links
        next_op = self.next_machine_op
        if next_op: next_op.pre_machine_op = None
        pre_op = op.pre_machine_op
        if pre_op: pre_op.next_machine_op = None

        # create new link
        self.next_machine_op = op
        op.pre_machine_op = self

    @property
    def top_job_op(self):
        '''The first operation step in current job chain.'''
        step = self
        while True:
            pre_step = step.pre_job_op
            if pre_step is None: return step
            step = pre_step

    @property
    def top_machine_op(self):
        '''The first operation step in current machine chain.'''
        step = self
        while True:
            pre_step = step.pre_machine_op
            if pre_step is None: return step
            step = pre_step

    @property
    def tail_job_op(self):
        '''The last step in current job chain.'''
        step = self
        while True:
            next_step = step.next_job_op
            if next_step is None: return step
            step = next_step

    @property
    def tail_machine_op(self):
        '''The last step in current machine chain.'''
        step = self
        while True:
            next_step = step.next_machine_op
            if next_step is None: return step
            step = next_step

    @property
    def machine_utilization(self):
        '''Utilization of the machine chain: service_time / (service_time + free_time).'''
        if not isinstance(self.source, Machine):
            raise JSPException('Only available for machine step.')

        service_time, total_time = 0.0, 0.0
        op = self.next_machine_op
        while op:
            service_time += op.source.duration
            total_time = op.end_time
            op = op.next_machine_op
        return service_time/total_time if total_time else 1.0
