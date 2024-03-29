'''Basic domain class: Job, Machine and Operation.'''


class Base:
    '''Base class with an index.'''
    def __init__(self, idx:int) -> None:
        self.id = idx


class Operation:
    '''Operation.'''

    def __init__(self,
                 job:"Job"=None,
                 machine:"Machine"=None,
                 duration:float=0.0) -> None:
        '''Operation instance.

        Args:
            job (Job): The job that this operation belonging to.
            machine (Machine): The machine that this operation assigned to.
            duration (float): The processing time.
        '''
        self.__machine = machine
        self.__job = job
        self.__duration = duration

    def __repr__(self) -> str:
        job_id = self.job.id if self.job else None
        machine_id = self.machine.id if self.machine else None
        return f'{self.__class__.__name__}({job_id}, {machine_id})'

    @property
    def job(self):
        '''Job instance.'''
        return self.__job

    @property
    def machine(self):
        '''Machine instance.'''
        return self.__machine

    @property
    def duration(self):
        '''Processing time.'''
        return self.__duration


class Job(Base, Operation):
    '''Job: a virtual operation.'''
    def __init__(self, idx:int):
        Base.__init__(self, idx)
        Operation.__init__(self, job=self)


class Machine(Base, Operation):
    '''Machine: a virtual operation.'''
    def __init__(self, idx:int):
        Base.__init__(self, idx)
        Operation.__init__(self, machine=self)


class Clone:
    '''Object with copyable attributes.'''

    def copy(self):
        '''Shallow copy of current instance.
        https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s12.html
        '''
        class Empty(self.__class__):
            '''Empty class inheriting from this class and do nothing when initializing.'''

        # change back to the same class
        new_copy = Empty()
        new_copy.__class__ = self.__class__

        # set same properties
        new_copy.__dict__.update(self.__dict__)
        return new_copy
