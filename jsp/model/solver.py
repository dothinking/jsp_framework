'''Base solver for Job-Shop Schedule Problem. '''

import time
import traceback
from abc import (ABC, abstractmethod)
from threading import (Thread, currentThread)
from .variable import OperationStep
from .problem import JSProblem
from .solution import JSSolution
from .domain import Clone
from ..common.exception import JSPException
from ..common.plot import (plot_gantt_chart_axes, plot_gantt_chart_bars)


class JSSolver(Clone, ABC):
    '''Solver.'''

    def __init__(self, name:str=None, problem:JSProblem=None, max_time:int=None) -> None:
        '''Base solver for Job-Shop Schedule Problem.

        Args:
            name (str, optional): Solver name. Default to None, i.e. class name.
            problem (JSProblem): Problem to solve.
            max_time (int, optional): Max solving time in seconds. Defaults to None, i.e., no limit.
        '''
        self.name = name or self.__class__.__name__
        self.__problem = problem
        self.__max_time = max_time

        # solving parameters
        self.__running = False
        self.__status = False
        self.__thread = None
        self.__user_time = 0.0

        # current solution
        self.__solution = None
        self.__need_update_chart = True # signal to update gantt chart
        self.__fun_callback = None      # user callback when better solution found


    @property
    def problem(self) -> JSProblem:
        '''Problem to solve.'''
        return self.__problem

    @problem.setter
    def problem(self, problem:JSProblem):
        '''Set problem.'''
        self.__solution = None
        self.__running = False
        self.__status = False
        self.__problem = problem

    @property
    def solution(self) -> JSSolution:
        '''Solution for problem to solve.'''
        return self.__solution

    @property
    def is_running(self):
        '''Whether the solver is running.'''
        return self.__running

    @property
    def status(self):
        '''Final status: True-success, False-failed or infeasible.'''
        return self.__status

    @property
    def max_time(self):
        '''Maximum time for solving process.'''
        return self.__max_time

    @property
    def user_time(self):
        '''Returns the solving time in seconds.'''
        return self.__user_time

    def wait(self):
        '''Wait the termination of solving process in child thread.'''
        self.__thread.join()

    def init_solution(self, direct_mode:bool=True):
        '''Initialize empty solution.'''
        if not self.problem: return None
        ops = [OperationStep(op) for op in self.problem.ops]
        return JSSolution(ops, direct_mode=direct_mode)

    def update_solution(self, solution):
        '''Set a better solution.

        Args:
            solution (JSSolution): A better solution.
        '''
        # update solution and run user defined function
        self.__solution = solution
        if self.__fun_callback: self.__fun_callback(solution)

        # signal to update gantt chart
        self.__need_update_chart = True


    def solve(self, interval:int=None, callback=None):
        '''Solve problem and update Gantt chart dynamically.

        Args:
            interval (int, optional): Gantt chart refresh interval (in ms). Defaults to None, i.e.,
                don not show Gantt chart.
            callback (function): User defined function called when a better solution is found.
                It takes a `JSSolution` instance as input.
        '''
        from matplotlib import pyplot as plt
        from matplotlib.animation import FuncAnimation

        if self.is_running:
            raise JSPException("There's already a solving process is running.")
        if not self.problem:
            raise JSPException("No problem to solve.")

        self.__user_time = time.perf_counter()
        self.__running = True
        self.__fun_callback = callback

        # solve problem in child thread
        self.__thread = Thread(target=self.__solving_thread,
                               name=f'{currentThread().name}_{self.name}')
        self.__thread.start()

        # show gantt chart and listen to the solution update in main thread
        if interval:
            fig, gnt_job, gnt_machine = plot_gantt_chart_axes(self.problem.jobs,
                                                              self.problem.machines,
                                                              self.problem.optimum)
            # animation: set attribute to keep alive
            self._gantt_animation = FuncAnimation(fig,
                                func=lambda i: self.__update_gantt_chart(gnt_job, gnt_machine),
                                interval=interval,
                                repeat=False)
            plt.show()


    @abstractmethod
    def do_solve(self):
        '''Inherit `JSSolver` and override this method to implement new solver.

        ```python
        def do_solve(self):
            """User defined solving process."""

            # (1) Initialize an empty solution and specify solving mode.
            # * direct_mode=True, solve start time directly;
            # * direct_mode=False, solve operations sequence first and deduce start time
            solution = self.init_solution(direct_mode=False)

            # (2) Solve or optimize the solution.
            for op in solution.ops:
                # option 1: solve and set start time directly
                ...
                op.update_start_time(solved_start_time)

                # option 2: # solve sequence
                ...
                self.dispatch(op)

            # (3) Update solution.
            # NOTE: call the following method when a better solution is found, which triggers
            # updating Gantt chart dynamically and running user defined callback.
            self.update_solution(solution)
        ```
        '''
        raise NotImplementedError('Not implemented solver.')


    def __solving_thread(self):
        '''Solve problem in child thread.'''
        try:
            self.do_solve()

        except JSPException:
            self.__status = False
            traceback.print_exc()

        else:
            self.__status = self.solution.is_feasible

        finally:
            self.__running = False
            self.__user_time = round(time.perf_counter()-self.__user_time, 1)


    def __update_gantt_chart(self, axis_job, axis_machine):
        '''Update Gantt chart with the best ever solution.'''
        if not self.__need_update_chart:  return
        # update gantt chart
        if self.solution:
            ops, makespan = self.solution.ops, self.solution.makespan
        else:
            ops, makespan = None, None
        plot_gantt_chart_bars(axis_job, axis_machine, ops, makespan)
        self.__need_update_chart = False
