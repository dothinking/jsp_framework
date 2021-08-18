'''Base solver for Job-Shop Schedule Problem. 
'''

import time
import traceback
from threading import Thread
from matplotlib import pyplot as plt
from .problem import JSProblem


class JSSolver:

    def __init__(self, name:str='base') -> None:
        '''Base solver for Job-Shop Schedule Problem.'''
        self.__running = False
        self.name = name
    

    def solve(self, problem:JSProblem, interval:int=2000, callback=None):
        '''Solve problem and update Gantt chart dynamically.
        
        Args:
            problem (JSProblem): Problem to solve.
            interval (int, optional): Gantt chart refresh interval (in ms). Defaults to 2000 ms.
            callback (function): User defined function called when a better solution is found.
                It takes a `JSSolution` instance as input.
        '''
        if self.__running:
            raise Exception("There's already a solving process is running.")
        else:
            self.__running = True        
        
        # solve problem in child thread
        thread = Thread(target=self.__solving_thread, args=(problem,))
        thread.start()

        # show gantt chart and listen to the solution update in main thread
        problem.dynamic_gantt(callback=callback, interval=interval)
        plt.show()


    def do_solve(self, problem:JSProblem):
        '''Inherit `JSSolver` and override this method to implement new solver.

        NOTE: call the following method when a better solution is found, which triggers updating 
        Gantt chart dynamically and running user defined callback.

        ```python
        # constructed or solved a solution
        solution = ...

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
        except Exception as e:
            traceback.print_exc()
            print('Solve process failed.')
        else:
            print(f'Terminate successfully in {round(time.time()-t0, 1)} sec.')
        finally:
            # terminate normally
            self.__running = False
