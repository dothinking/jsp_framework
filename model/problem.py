'''Job-Shop Schedule Problem.
'''

import os
import json
import random
from .domain import Job, Machine, Operation


class JSProblem:
    '''Base class for Job Shop Schedule Problem.
    '''

    def __init__(self, jobs:list=None, 
                        num_jobs:int=0, num_machines:int=0, 
                        benchmark:str=None, 
                        input_file:str=None) -> None:
        """Initialize problem by job list, or random problem with specified count of jobs 
        and machines, or just load data from benchmark/user-defined file. 
        
        In addition, job chain (the sequence of job operations) is created.

        Args:
            jobs (list, optional): Job list to schedule. 
            num_jobs (int, optional): Initialize random problem by specified count of jobs. 
            num_machines (int, optional): Initialize random problem by specified count of machines. 
            benchmark (str, optional): Benchmark name to load associated data.
            input_file (str, optional): User defined data file path. 
        """        
        self.__operations = None   # type: list[Operation]

        # benchmark only
        self.__optimum = None      # type: float

        # load jobs directly
        self.__jobs = []           # type: list[Job]
        if jobs:
            self.__jobs = jobs

        # random jobs
        elif num_jobs and num_machines:
            self.__jobs = self.__generate_random_jobs(num_jobs, num_machines)
        
        # jobs from benchmark
        elif benchmark:
            self.__jobs = self.__load_benchmark_jobs(name=benchmark)
        
        # jobs from user input file
        elif input_file:
            self.__jobs = self.__load_jobs(input_file)
            

        # create operation sequence with each job
        self.__create_job_chain()


    
    @property
    def optimum(self): return self.__optimum    
    
    @property
    def jobs(self): return self.__jobs

    @property
    def operations(self): return self.__operations

    @property
    def machines(self):
        machines = list(set(op.machine for op in self.__operations))
        machines.sort(key=lambda machine: machine.id)
        return machines


    def __load_benchmark_jobs(self, name:str) -> list:
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
                else:
                    self.__optimum = (instance['bounds']['lower'], instance['bounds']['upper'])
                break
        else:
            raise Exception(f'Cannot find benchmark name: {name}.')
        
        # load jobs
        return self.__load_jobs(os.path.join(benchmark_path, filename))
   

    def __load_jobs(self, filename:str) -> list:
        '''Load jobs from formatted data file.'''
        if not os.path.exists(filename):
            raise Exception(f'Cannot find data file: {filename}.')
        
        # load lines and skip comment line starting with #
        with open(filename, 'r') as f:
            lines = [line for line in f.readlines() if not line.startswith('#')]
        
        # first line: jobs-count machines-count
        num_jobs, num_machines = lines[0].strip().split()
        machines = [Machine(i) for i in range(num_machines)]

        # create a job per line
        jobs = []
        for n, line in enumerate(lines[1:num_jobs+1]):
            ops = []
            fields = list(map(int, line.strip().split()))
            for i in range(num_machines):
                op = Operation(i, machine=machines[fields[2*i]], duration=fields[2*i+1])
                ops.append(op)
            
            # create job
            jobs.append(Job(n, ops))
        
        return jobs


    def __generate_random_jobs(self, num_jobs:int, num_machines:int) -> list:
        '''Generate random jobs with specified count of machine and job.'''
        # machine list
        machines = [Machine(i) for i in range(num_machines)]

        # job list
        jobs = []
        for i in range(num_jobs):
            random.shuffle(machines)
            job = Job(i)
            job.add_random_ops(machines)
            jobs.append(job)
        
        return jobs


    def __create_job_chain(self):
        '''Create sequence of operations.'''
        for job in self.__jobs: 
            job.create_chain()



    


    

