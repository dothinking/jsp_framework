'''Basic domain class: Job, Machine and Operation.
'''


class Base:    
    def __init__(self, id:int) -> None:
        '''An instance with an ID.'''
        self.id = id
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id})'


class Job(Base):
    
    def __init__(self, id:int) -> None:
        '''Job instance.'''
        super().__init__(id)
    
    
class Machine(Base):
    
    def __init__(self, id:int) -> None:
        '''Machine instance.
        '''
        super().__init__(id)


class Operation(Base):

    def __init__(self, id:int, job:Job, machine:Machine, duration:float) -> None:
        '''Operation instance.

        Args:
            id (int): Operation ID.
            job (Job): The job that this operation belonging to.
            machine (Machine): The machine that this operation assigned to.
            duration (float): The processing time.
        '''
        super().__init__(id)

        # properties: keep constant
        self.__machine = machine
        self.__job = job
        self.__duration = duration


    @property
    def job(self): return self.__job

    @property
    def machine(self): return self.__machine

    @property
    def duration(self): return self.__duration