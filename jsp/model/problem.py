'''Job-Shop Schedule Problem.'''
import os
import json
import random
from typing import List
from .domain import (Job, Machine, Operation)
from ..common.exception import JSPException


class JSProblem:
    '''Base class for Job Shop Schedule Problem.'''

    def __init__(self, ops:List[Operation]=None,
                        num_jobs:int=0, num_machines:int=0,
                        benchmark:str=None,
                        input_file:str=None,
                        name:str=None) -> None:
        '''Initialize problem by operation list, or random problem with specified count of jobs
        and machines, or just load data from benchmark/user-defined file.

        Args:
            ops (list, optional): Operation list to schedule. Note that the order indicates
                operation sequence in job chain.
            num_jobs (int, optional): Initialize random problem by specified count of jobs.
            num_machines (int, optional): Initialize random problem by specified count of machines.
            benchmark (str, optional): Benchmark name to load associated data.
            input_file (str, optional): User defined data file path.
            name (str, optional): Problem name. Benchmark name if None.
        '''
        self.name = name

        # # benchmark value of solution
        self.__optimum = None

        # initialize operations
        self.__ops = []   # type: list[Operation]
        if ops:
            self.__ops = ops

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
    def jobs(self) -> List[Job]:
        '''All jobs.'''
        return self.__jobs

    @property
    def machines(self) -> List[Machine]:
        '''All machines.'''
        return self.__machines

    @property
    def ops(self) -> List[Operation]:
        '''All operations.'''
        return self.__ops

    @property
    def optimum(self):
        '''Optimized value from benchmark case.'''
        return self.__optimum


    def __collect_jobs_and_machines(self):
        if not self.ops: return None, None
        jobs, machines = zip(*((op.job, op.machine) for op in self.ops))
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
        path_instances = os.path.join(benchmark_path, 'instances.json')
        with open(path_instances, 'r', encoding='utf-8') as f:
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
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line for line in f.readlines() if not line.startswith('#')]

        # first line: jobs-count machines-count
        num_jobs, num_machines = map(int, lines[0].strip().split())
        machines = [Machine(i) for i in range(num_machines)]
        jobs = [Job(i) for i in range(num_jobs)]

        # one job per line
        ops = []
        for line, job in zip(lines[1:num_jobs+1], jobs):
            fields = list(map(int, line.strip().split()))
            for j in range(num_machines):
                op = Operation(job=job,
                                machine=machines[fields[2*j]],
                                duration=fields[2*j+1])
                ops.append(op)
        return ops


    def __generate_by_random(self, num_jobs:int, num_machines:int) -> list:
        '''Generate random jobs with specified count of machine and job.'''
        # job list and machine list
        machines = [Machine(i) for i in range(num_machines)]
        jobs = [Job(i) for i in range(num_jobs)]

        # random operations
        ops = []
        lower, upper = 10, 50
        for job in jobs:
            random.shuffle(machines)
            for machine in machines:
                duration = random.randint(lower, upper)
                op = Operation(job=job, machine=machine, duration=duration)
                ops.append(op)
        return ops
