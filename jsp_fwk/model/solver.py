'''Base solver for Job-Shop Schedule Problem. 
'''

import time
import traceback
from threading import (Thread, currentThread)
from matplotlib import pyplot as plt
from .problem import JSProblem
from .domain import Cloneable
from ..common.exception import JSPException


class JSSolver(Cloneable):

    def __init__(self, name:str=None) -> None:
        '''Base solver for Job-Shop Schedule Problem.

        Args:
            name (str, optional): Solver name. Default to None, i.e. class name.
        '''
        self.name = name or self.__class__.__name__
        self.__running = False
        self.__status = False
        self.__thread = None
        self.__user_time = time.perf_counter()

    @property
    def is_running(self): return self.__running

    @property
    def status(self): return self.__status

    @property
    def user_time(self):
        '''Returns the user time in seconds since the creation of the solver.'''
        return self.__user_time    

    def wait(self):
        '''Wait the termination of solving process in child thread.'''
        self.__thread.join()
    

    def solve(self, problem:JSProblem, interval:int=None, callback=None):
        '''Solve problem and update Gantt chart dynamically.
        
        Args:
            problem (JSProblem): Problem to solve.
            interval (int, optional): Gantt chart refresh interval (in ms). Defaults to None, i.e. 
                don not show Gantt chart.
            callback (function): User defined function called when a better solution is found.
                It takes a `JSSolution` instance as input.
        '''
        if self.__running:
            raise JSPException("There's already a solving process is running.")
        else:
            self.__running = True
        
        # call user function when better solution is found
        if callback:
            problem.register_solution_callback(callback=callback)
        
        # solve problem in child thread
        self.__thread = Thread(target=self.__solving_thread, args=(problem,), \
                                name=f'{currentThread().name}_{self.name}')
        self.__thread.start()

        # show gantt chart and listen to the solution update in main thread
        if interval:
            problem.dynamic_gantt(interval=interval)
            plt.show()


    def do_solve(self, problem:JSProblem):
        '''Inherit `JSSolver` and override this method to implement new solver.

        ```python
        def do_solve(self, problem:JSProblem):
            """User defined solving process."""

            # (1) Initialize an empty solution from problem
            solution = JSSolution(problem)

            # (2) Solve or optimize the solution, 
            # i.e. determine the start_time of OperationStep instances.
            # Note to evaluate solution explicitly if disjunctive graph model.
            ...
            # solution.evaluate() 

            # (3) Update the solution for problem iteratively
            # NOTE: call the following method when a better solution is found, which triggers 
            # updating Gantt chart dynamically and running user defined callback.
            problem.update_solution(solution)
        ```

        Args:
            problem (JSProblem): Problem to solve.
        '''
        raise NotImplementedError('Not implemented solver.')    


    def __solving_thread(self, problem:JSProblem):
        '''Solve problem in child thread.'''
        try:
            self.do_solve(problem=problem)

        except JSPException:
            self.__status = False
            traceback.print_exc()
        
        else:
            self.__status = problem.solution.is_feasible()
            
        finally:
            self.__running = False
            self.__user_time = round(time.perf_counter()-self.__user_time, 1)