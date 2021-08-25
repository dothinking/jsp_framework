import logging
import threading
from queue import Queue
from prettytable import PrettyTable


# logging
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s %(threadName)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')


class BenchMark:

    def __init__(self, problems:list, solvers:list, num_threads:int=4) -> None:
        '''Solve a list of problem with a list of solvers, respectively.

        Args:
            problems (list): Problems list to solve.
            solvers (list): Solvers list to solve the problem.
            num_threads (int, optional): Number of threads to run the benchmark.
        '''
        self.__num_threads = num_threads

        # all cases to solve: (problem, solver)
        self.__solving_queue = Queue(maxsize=len(problems)*len(solvers))
        i = 0 # indicating the order
        for problem in problems:
            for solver in solvers:
                self.__solving_queue.put((i, problem.copy(), solver.copy()))
                i += 1
        
        # solvered cases: [(id, problem, solver), ...]
        self.__solved_cases = []

    @property
    def result(self): return self.__solved_cases


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
            thread = threading.Thread(target=self.__solve_one_case, args=(show_info, fun_callback), \
                name=f'Runner_{i}')
            thread.setDaemon(True) # terminate this child thread when the main thread terminates
            thread.start()

        # wait for termination
        self.__solving_queue.join()

        # sort result cases by id
        self.__solved_cases.sort(key=lambda case: case[0])

        # print final results
        if show_info: logging.info(f'\n{self.summary()}')


    def summary_list(self) -> list:
        '''Collect benchmark results in list: 
        [
            [index, problem name, solver name, problem scale, optimum, calculated value, error, spent time],
            ...,
        ]        

        Args:
            solved_cases (list): A list of solved cases: (problem, solver).
        '''
        res = []
        for (i, p, s) in self.__solved_cases:
            optimum = p.optimum
            cal_value = p.solution.makespan
            ref = (optimum[0]+optimum[1])/2 if isinstance(optimum, tuple) else optimum
            case = [i+1, p.name, s.name, f'{len(p.jobs)} x {len(p.machines)}', optimum, \
                        cal_value, round((cal_value/ref-1)*100,1), s.user_time]
            res.append(case)

        return res
    

    def summary(self) -> str:
        '''Output benchmark result in tabular format.'''
        table = PrettyTable()

        # title
        table.field_names = ['ID', 'Problem','Solver','job x machine','Optimum', 'Solution', 'Error %', 'Time']

        # data
        for line in self.summary_list(): table.add_row(line)

        return table


    def __solve_one_case(self, show_info, callback):
        '''Solve one case in child thread.'''
        while True:
            i, problem, solver = self.__solving_queue.get()

            # start solving
            if show_info:
                logging.info(f'Start solving "{problem.name}" with "{solver.name}"...')
            solver.solve(problem=problem, interval=None, callback=callback) # don't show gantt chart
            solver.wait() # wait for termination

            # collect results
            self.__solved_cases.append((i, problem, solver))
            self.__solving_queue.task_done()
            if show_info:
                logging.info(f'{"Successfully" if solver.status else "Failed"} to solve "{problem.name}" with "{solver.name}" in {solver.user_time} sec.')
    

    