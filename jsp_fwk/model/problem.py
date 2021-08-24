'''Job-Shop Schedule Problem.
'''

import os
import json
import random
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from .domain import (Job, Machine, Operation, Cloneable)
from ..common.exception import JSPException


class JSProblem(Cloneable):
    '''Base class for Job Shop Schedule Problem.
    '''

    def __init__(self, ops:list=None, 
                        num_jobs:int=0, num_machines:int=0, 
                        benchmark:str=None, 
                        input_file:str=None,
                        name:str=None) -> None:
        '''Initialize problem by operation list, or random problem with specified count of jobs 
        and machines, or just load data from benchmark/user-defined file. 

        Args:
            ops (list, optional): Operation list to schedule. 
            num_jobs (int, optional): Initialize random problem by specified count of jobs. 
            num_machines (int, optional): Initialize random problem by specified count of machines. 
            benchmark (str, optional): Benchmark name to load associated data.
            input_file (str, optional): User defined data file path. 
            name (str, optional): Problem name. Benchmark name if None. 
        '''
        self.name = name
        
        # solution
        self.__solution = None          # to solve  
        self.__optimum = None           # benchmark value
        self.__solution_callback = None   # callback when a better solution is found

        # dynamic Gantt chart
        self.__gantt_animation = None
        self.__need_update_chart = False # update chart when found a better solution

        # initialize operations
        self.__ops = []   # type: list[Operation]
        if ops: self.__ops = ops

        # random operations
        elif num_jobs and num_machines:
            self.__ops = self.__generate_by_random(num_jobs, num_machines)
        
        # from benchmark
        elif benchmark:
            self.__ops = self.__load_from_benchmark(name=benchmark)
            if not name: self.name = benchmark
        
        # from user input file
        elif input_file:
            self.__ops = self.__load_from_file(input_file)            

        # collect jobs and machines
        self.__jobs, self.__machines = self.__collect_jobs_and_machines()
        
    
    
    @property
    def jobs(self): return self.__jobs

    @property
    def machines(self): return self.__machines

    @property
    def ops(self): return self.__ops

    @property
    def optimum(self): return self.__optimum

    @property
    def solution(self): return self.__solution


    def register_solution_callback(self, callback):
        '''Register solution callback called when a better solution is found.'''
        self.__solution_callback = callback


    def update_solution(self, solution):
        '''Set a better solution.

        Args:
            solution (JSSolution): A better solution. 
        '''
        # update solution and run user defined function
        self.__solution = solution
        if self.__solution_callback: self.__solution_callback(solution)

        # signal to update gantt chart
        self.__need_update_chart = True


    def dynamic_gantt(self, interval:int=2000):
        '''Initialize empty Gantt chart with `matplotlib` and update it dynamically.

        Args:
            
            interval (int, optional): Refresh interval (in ms). Defaults to 2000 ms.
        '''
        # two subplots
        fig, (gnt_job, gnt_machine) = plt.subplots(2,1, sharex=True)

        # title and sub-title
        fig.suptitle('Gantt Chart', fontweight='bold')
        if self.__optimum is not None:
            gnt_job.set_title(f'Optimum: {self.__optimum}', color='gray', fontsize='small')

        # axes style        
        gnt_job.set(ylabel='Job', \
            yticks=range(len(self.__jobs)), \
            yticklabels=[f'J-{job.id}' for job in self.__jobs])
        gnt_job.grid(which='major', axis='x', linestyle='--')
        
        gnt_machine.set(xlabel='Time', ylabel='Machine',\
            yticks=range(len(self.__machines)), \
            yticklabels=[f'M-{machine.id}' for machine in self.__machines])
        gnt_machine.grid(which='major', axis='x', linestyle='--')

        # animation
        self.__gantt_animation = FuncAnimation(fig, \
            func=lambda i: self.__update_gantt_chart(axes=(gnt_job, gnt_machine)), \
            interval=interval, \
            repeat=False)
    

    def __update_gantt_chart(self, axes:tuple):
        if not self.__need_update_chart: 
            return
        else:
            self.__need_update_chart = False

        # update gantt chart
        self.__solution.plot(axes)


    def __collect_jobs_and_machines(self):
        jobs, machines = zip(*((op.job, op.machine) for op in self.__ops))
        jobs = sorted(set(jobs), key=lambda job: job.id)
        machines = sorted(set(machines), key=lambda machine: machine.id)
        return jobs, machines


    def __load_from_benchmark(self, name:str) -> list:
        '''Load jobs and optimum value from benchmark data.'''
        # benchmark path
        script_path = os.path.abspath(__file__)
        prj_path = os.path.dirname(os.path.dirname(script_path))
        benchmark_path = os.path.join(prj_path, 'benchmark')

        # check benchmark name
        with open(os.path.join(benchmark_path, 'instances.json'), 'r') as f:
            instances = json.load(f)        
        for instance in instances:
            if instance['name']==name:
                filename = instance['path']
                if instance['optimum']:
                    self.__optimum = instance['optimum']
                elif instance['bounds']:
                    self.__optimum = (instance['bounds']['lower'], instance['bounds']['upper'])
                break
        else:
            raise JSPException(f'Cannot find benchmark name: {name}.')
        
        # load jobs
        return self.__load_from_file(os.path.join(benchmark_path, filename))
   

    def __load_from_file(self, filename:str) -> list:
        '''Load jobs from formatted data file.'''
        if not os.path.exists(filename):
            raise JSPException(f'Cannot find data file: {filename}.')
        
        # load lines and skip comment line starting with #
        with open(filename, 'r') as f:
            lines = [line for line in f.readlines() if not line.startswith('#')]
        
        # first line: jobs-count machines-count
        num_jobs, num_machines = map(int, lines[0].strip().split())
        machines = [Machine(i) for i in range(num_machines)]
        jobs = [Job(i) for i in range(num_jobs)]

        # one job per line
        ops = []
        i = 0
        for line, job in zip(lines[1:num_jobs+1], jobs):
            fields = list(map(int, line.strip().split()))
            for j in range(num_machines):
                op = Operation(id=i, job=job, machine=machines[fields[2*j]], duration=fields[2*j+1])
                ops.append(op)
                i += 1
        
        return ops


    def __generate_by_random(self, num_jobs:int, num_machines:int) -> list:
        '''Generate random jobs with specified count of machine and job.'''
        # job list and machine list
        machines = [Machine(i) for i in range(num_machines)]
        jobs = [Job(i) for i in range(num_jobs)]

        # random operations
        ops = []
        i = 0
        lower, upper = 10, 50
        for job in jobs:
            random.shuffle(machines)
            for machine in machines:
                duration = random.randint(lower, upper)
                op = Operation(id=i, job=job, machine=machine, duration=duration)
                ops.append(op)
                i += 1
        
        return ops    

