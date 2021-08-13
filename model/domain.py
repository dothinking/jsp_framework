'''Basic domain class: Machine and Operation.
'''
import random



class Step:
    '''A virtual step representing a machine or an operation.
    '''
    def __init__(self, id:int) -> None:
        self.id = id
        # machine chain to solve
        self.__pre_op = None   # type: Step
        self.__next_op = None   # type: Operation
    
    @property
    def pre_op(self): return self.__pre_op

    @property
    def next_op(self): return self.__next_op

    @pre_op.setter
    def pre_op(self, op):
        self.__pre_op = op
        if op is not None: op.__next_op = self
    
    @property
    def end_time(self) -> float: 
        '''Ready time of this step. '''
        return NotImplementedError



class Machine(Step):
    '''The machine.'''
    def __init__(self, id: int) -> None:
        super().__init__(id)

    @property
    def end_time(self) -> float: 
        '''A machine is always ready. '''
        return 0.0


class Operation(Step):
    '''The operation.'''
    def __init__(self, id:int, machine:Machine, duration:float, parent=None) -> None:
        super().__init__(id)
        # properties: keep constant
        self.__machine = machine
        self.__duration = duration
        self.parent = parent

        # job chain
        self.__pre_job_op = None   # type: Operation
        self.__next_job_op = None   # type: Operation        

        # shadow variable
        self.__start_time = 0.0


    @property
    def machine(self): return self.__machine

    @property
    def duration(self): return self.__duration

    @property
    def start_time(self) -> float: return self.__start_time

    @property
    def end_time(self) -> float: return self.__start_time + self.__duration

    @property
    def pre_job_op(self): return self.__pre_job_op

    @property
    def next_job_op(self): return self.__next_job_op

    @pre_job_op.setter
    def pre_job_op(self, op:Step):
        self.__pre_job_op = op
        if op is not None: op.__next_job_op = self


    def update_start_time(self):
        '''Update start time: the late start time in job chain and machine chain.'''
        self.__start_time = max(self.__job_chain_start_time(), \
            self.__machine_chain_start_time())
    

    def copy(self):
        '''Copy to a new instance with same properties. Keep same job chain sequence.'''
        op = Operation(self.id, self.__machine, self.__duration, self.parent)
        op.__pre_job_op = self.__pre_job_op
        op.__next_job_op = self.__next_job_op
        return op


    def __job_chain_start_time(self) -> float:
        '''The earlist start time in job chain. It's right after the end time of previous operation;
        or start immediately if this is the first operation.'''
        if self.pre_job_op is None:
            return 0.0
        else:
            return self.pre_job_op.end_time
    

    def __machine_chain_start_time(self):
        '''The earlist start time in machine chain, i,e, the end time of previous step in machine chain.
        Note the machine itself would be a virtual step.
        '''
        return self.pre_op.end_time
    

class Job:
    '''A collection of sequent operations.'''
    def __init__(self, ops:list=None) -> None:
        '''Initialize job with operation list.'''
        self.__ops = []  # type: list[Operation]
        for op in (ops or []):
            op.parent = self
            self.__ops.append(op)
    

    def add_random_ops(self, machines:list, lower_duration:float=5, upper_duration:float=30):
        '''Add random operations based on steps defined by machine list.

        Args:
            machines (list): Machine list defines the sequence of operations.
            lower_duration (float, optional): Lower bound of operation duration. Defaults to 5.
            upper_duration (float, optional): Upper bound of operation duration. Defaults to 30.
        '''
        for i, machine in enumerate(machines):
            duration = random.randint(int(lower_duration), int(upper_duration))
            self.__ops.append(Operation(i, machine, duration, parent=self))


    def create_chain(self):
        '''Create sequence of operations.'''
        pre = None
        for op in self.__ops:
            op.pre_job_op = pre
            pre = op