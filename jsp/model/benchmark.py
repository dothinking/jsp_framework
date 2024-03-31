'''Test multiple solvers on multiple problems.'''
from typing import (List, Tuple)
import logging
import threading
from queue import Queue
from prettytable import PrettyTable
from .problem import JSProblem
from .solver import JSSolver


# logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(threadName)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')


class BenchMark:
    '''Solvers benchmark.'''

    def __init__(self, problems:List[JSProblem], solvers:List[JSSolver], num_threads:int=4) -> None:
        '''Solve a list of problem with a list of solvers, respectively.

        Args:
            problems (list): Problems list to solve.
            solvers (list): Solvers list to solve the problem.
            num_threads (int, optional): Number of threads to run the benchmark.
        '''
        self.__num_threads = num_threads

        # all cases to solve: (index, solver)
        self.__solving_queue = Queue(maxsize=len(problems)*len(solvers))
        i = 0 # indicating the order
        for problem in problems:
            for solver in solvers:
                s = solver.copy()
                s.problem = problem
                self.__solving_queue.put((i, s))
                i += 1
        # solved cases: [(id, solver), ...]
        self.__solved_cases = []


    @property
    def result(self) -> List[Tuple[int,JSSolver]]:
        '''solved cases: [(id, solver), ...].'''
        return self.__solved_cases


    def run(self, show_info:bool=True, callback=None):
        '''Run benchmark with specified problems and solvers.

        Args:
            show_info (bool, optional): Show information during solving process. Defaults to True.
            callback (function, optional): User defined function called during each iteration.
                Defaults to None.
        '''
        fun_callback = callback if show_info else None
        # create child threads
        for i in range(self.__num_threads):
            thread = threading.Thread(target=self.__solve_one_case,
                                      args=(show_info, fun_callback),
                                      name=f'Runner_{i}')
            thread.setDaemon(True) # terminate this child thread if the main thread terminates
            thread.start()

        # wait for termination
        self.__solving_queue.join()

        # sort result cases by id
        self.result.sort(key=lambda case: case[0])

        # print final results
        if show_info: logging.info('\n%s', self.summary())


    def summary_list(self) -> list:
        '''Collect benchmark results in list:
        [
            [index, problem name, solver name, problem scale,
                        optimum, calculated value, error, spent time],
            ...,
        ]
        '''
        res = []
        for (i, s) in self.result:
            # benchmarking
            p = s.problem
            optimum = p.optimum
            ref = (optimum[0]+optimum[1])/2 if isinstance(optimum, tuple) else optimum

            # solved
            if s.solution and s.solution.is_feasible:
                cal_value = s.solution.makespan
                err = round((cal_value/ref-1)*100,1)
            else:
                cal_value = 'unsolved'
                err = 'n.a.'

            case = [i+1, p.name, s.name, f'{len(p.jobs)} x {len(p.machines)}', optimum, \
                        cal_value, err, s.user_time]
            res.append(case)
        return res


    def summary(self) -> str:
        '''Output benchmark result in tabular format.'''
        table = PrettyTable()

        # title
        table.field_names = ['ID', 'Problem', 'Solver', 'job x machine',
                             'Optimum', 'Solution', 'Error %', 'Time']

        # data
        for line in self.summary_list(): table.add_row(line)
        return table


    def __solve_one_case(self, show_info, callback):
        '''Solve one case in child thread.'''
        while True:
            i, solver = self.__solving_queue.get()
            p = solver.problem

            # start solving
            if show_info:
                logging.info('Start solving "%s" with "%s"...', p.name, solver.name)
            solver.solve(interval=None, callback=callback) # don't show gantt chart
            solver.wait() # wait for termination

            # collect results
            self.__solved_cases.append((i, solver))
            self.__solving_queue.task_done()
            if show_info:
                res = "Successfully" if solver.status else "Failed"
                logging.info('%s to solve "%s" with "%s" in %f sec.',
                             res, p.name, solver.name, solver.user_time)
