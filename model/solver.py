'''Base solver for Job-Shop Schedule Problem. 
'''

import time
import traceback
from threading import Thread
from matplotlib import pyplot as plt
from .problem import JSProblem
from common.exception import JSPException


class JSSolver:

    def __init__(self) -> None:
        '''Base solver for Job-Shop Schedule Problem.'''
        self.__running = False
    

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
        thread = Thread(target=self.__solving_thread, args=(problem,))
        thread.start()

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
        t0 = time.time()
        # solve problem
        try:
            self.do_solve(problem=problem)
        except JSPException:
            traceback.print_exc()
            print('Solving process failed.')
        else:
            print(f'Terminate successfully in {round(time.time()-t0, 1)} sec.')
        finally:
            # terminate normally
            self.__running = False
