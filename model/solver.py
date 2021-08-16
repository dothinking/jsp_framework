'''Base solver for Job-Shop Schedule Problem.
'''

from collections import defaultdict
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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
        self.__running = False
        self.name = name
        self.callback = callback or self.__default_callback
    

    def solve(self, problem:JSProblem):
        '''Solve problem in child thread.'''
        if self.__running:
            raise Exception("There's already a solving process is running.")
        else:
            self.__running = True        
        
        # plot gantt chart
        # self.__axes = problem.gantt()
        # self.ani = FuncAnimation(plt.gcf(), self.run, interval = 10, repeat=True)

        import time
        time.sleep(3)
        
        # solve problem in child thread
        thread = Thread(target=self.__solving_thread, args=(problem,))
        try:
            thread.start()
        except:
            self.__running = False
        
    

    
    

    def __solving_thread(self, problem:JSProblem):
        # solving
        solution = self.__solve(problem=problem)

        # evalute the solution
        problem.solution = solution
        solution.evaluate(callback=self.callback)

        # terminate normally
        self.__running = False


    def __solve(self, problem:JSProblem) -> JSSolution:
        '''A default solving process to determin the sequence of operations by job id for operations
        assigned to each machine.
        '''
        solution = JSSolution(problem)

        # group operations by machine
        machine_chains = defaultdict(list)
        for op in solution.ops:
            machine_chains[op.source.machine].append(op)
        
        # sort by job id, then create chain accordingly
        def create_chain(ops:list):
            pre = None
            for op in ops:
                op.pre_machine_op = pre
                pre = op

        for machine, ops in machine_chains.items():
            ops.sort(key=lambda op: op.source.job.id)
            create_chain(ops)
            solution.evaluate(callback=self.callback)
            problem.solution = solution
        
        return solution    
        


    def __default_callback(self, solution:JSSolution):
        '''Plot Gantt chart.'''
        print('-----')
        # solution.plot(self.__axes)