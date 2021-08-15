'''Basic domain class: Machine and Operation.
'''


class Step:    
    def __init__(self, id:int) -> None:
        '''An instance with an ID.'''
        self.id = id
    
    @property
    def end_time(self) -> float: 
        '''The complete time of this step. '''
        raise NotImplementedError("Method not implemented.")


class Collection:
    def __init__(self) -> None:
        '''An instance consists of sequent operations.'''
        self.__ops = []  # type: list[Operation]

    @property
    def ops(self): return self.__ops

    def create_chain(self):
        '''Create chain according to the sequence of operations.'''
        raise NotImplementedError("Method not implemented.")


class JobStep(Step):
    
    def __init__(self, id:int) -> None:
        '''A step in job chain. 
        A job itself is a virtual step at the beginning of the job chain.
        '''
        super().__init__(id)
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
    
    
class MachineStep(Step):
    
    def __init__(self, id:int) -> None:
        '''A step in machine chain. 
        A machine itself is a virtual step at the beginning of the machine chain.
        '''
        super().__init__(id)
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


class Job(JobStep, Collection):

    def __init__(self, id:int) -> None:
        '''Initialize job with an empty operation list (to add operations later).
        A job is a virtual step in job chain; in addition, a collection of sequent 
        operations.

        NOTE: this sequence of job operations is constant.
        '''
        JobStep.__init__(id)
        Collection.__init__()

    def create_chain(self):
        '''Create job chain according to the sequence of operations.'''
        pre = self
        for op in self.__ops:
            op.pre_job_op = pre
            pre = op
    
    @property
    def end_time(self) -> float: 
        '''A job is always ready. '''
        return 0.0



class Machine(MachineStep, Collection):

    def __init__(self, id: int) -> None:
        '''Initialize machine with an empty operation list (to add operations later).
        A machine is a virtual step in machine chain; in addition, a collection of sequent 
        operations assigned to. 
        
        NOTE: The solving process is to determin the sequence of operations assigned to this
        machine.
        '''
        MachineStep.__init__(id)
        Collection.__init__()    

    def create_chain(self):
        '''Create machine chain according to the sequence of operations.'''
        pre = self
        for op in self.__ops:
            op.pre_machine_op = pre
            pre = op

    @property
    def end_time(self) -> float: 
        '''A machine is always ready. '''
        return 0.0


class Operation(JobStep, MachineStep):

    def __init__(self, id:int, job:Job, machine:Machine, duration:float) -> None:
        '''An operation has to two kinds of sequence chain: a job chain and a machine chain.
        A job chain is the sequence of operations to complete a job, which is constant in 
        Job-Shop problem; while a machine chain the sequence of operations assigned to a same
        machine, which is to be solved.

        Args:
            id (int): Operation ID.
            job (Job): The job that this operation belonging to.
            machine (Machine): The machine that this operation assigned to.
            duration (float): The processing time.
        '''
        JobStep.__init__(id)
        MachineStep.__init__(id)

        # properties: keep constant
        self.__machine = machine
        self.__job = job
        self.__duration = duration

        # shadow variable
        self.__start_time = 0.0

    @property
    def job(self): return self.__job

    @property
    def machine(self): return self.__machine

    @property
    def duration(self): return self.__duration

    @property
    def start_time(self) -> float: return self.__start_time

    @property
    def end_time(self) -> float: return self.__start_time + self.__duration


    def update_start_time(self):
        '''Update start time: the late start time in job chain and machine chain.'''
        self.__start_time = max(self.pre_job_op.end_time, self.pre_op.end_time)
    

    def copy(self):
        '''Copy to a new instance with same properties. Keep same job chain sequence.'''
        op = Operation(self.id, self.__job, self.__machine, self.__duration)
        op.__pre_job_op = self.__pre_job_op
        if self.__next_job_op:
            self.__next_job_op.pre_job_op = op
        return op