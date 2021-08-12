'''Job-Shop Schedule Problem.
'''



class JSProblem:
    '''Base class for Job Shop Schedule Problem.
    '''

    def __init__(self, ops:list) -> None:
        self.__operations = ops