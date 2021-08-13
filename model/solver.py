'''Base solver for Job-Shop Schedule Problem.
'''

from .problem import JSProblem
from .solution import JSSolution


class JSSolver:

    def __init__(self, name:str, callback=None) -> None:
        '''Base solver for Job-Shop Schedule Problem.

        Args:
            name (str): Solver name.
            callback (function): User defined function called when a better solution is found.
                It takes a `JSSolution` instance as input.
        '''
        self.name = name
        self.callback = callback or self.__default_callback

    
    def solve(self, problem:JSProblem) -> JSSolution:
        pass


    def __default_callback(self, solution:JSSolution):
        pass