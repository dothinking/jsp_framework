'''Genetic Algorithm solver with geatpy.

```
pip install geatpy
```
'''
from typing import List
from abc import (ABC, abstractmethod)
from collections import defaultdict
import numpy as np
import geatpy as ea
from ..model.variable import OperationStep
from ..model.solver import JSSolver
from ..model.problem import JSProblem
from ..model.solution import JSSolution


class GeatpyProblem(ea.Problem):
    '''Geatpy problem.'''

    def __init__(self,
                 name:str,
                 var_type:int,
                 dim:int,
                 lb:List[float],
                 ub:List[float],
                 solver:"IGeatpySolver") -> None:
        '''Geatpy problem.

        Args:
            name (str): problem name.
            var_type (int): variable type, 0-continuous, 1-integer.
            dim (int): variables dimension.
            lb (float): low bounds
            ub (float): upper bounds.
            solver (JSSolver): solver.
        '''
        self.__solver = solver
        super().__init__(name=name,
                         M=1, # number of objectives
                         maxormins=[1],  # 1：minimize, -1-maximize
                         Dim=dim,
                         varTypes=[var_type]*dim, # 0-continuous, 1-integer
                         lb=lb,
                         ub=ub,
                         lbin=[1]*dim,
                         ubin=[1]*dim)


    def evalVars(self, inputs:np.ndarray):
        '''Objective function.'''
        solutions =  [self.__solver.decode(x=x) for x in inputs]
        cost = np.array([p.makespan for p in solutions])
        return cost.reshape((-1,1)) # shape: (m,n)


class IGeatpySolver(JSSolver, ABC):
    '''Genetic Algorithm solver with geatpy.'''

    def __init__(self,
                 name:str=None,
                 problem:JSProblem=None,
                 encoding:str='P',
                 pop_size:int=32,
                 epoch:int=None,
                 max_time:int=None) -> None:
        '''GA solver with geatpy.

        Args:
            name (str, optional): solver name. Defaults to None.
            problem (JSProblem, optional): problem to solve. Defaults to None.
            encoding (str, optional): geatpy GA encoding.
            pop_size (int, optional): population size. Defaults to 32.
            epoch (int, optional): max generation. Defaults to 10.
            max_time (int, optional): Max solving time in seconds. Defaults to None, i.e., no limit.
        '''
        JSSolver.__init__(self, name=name, problem=problem, max_time=max_time)
        self.__pop_size = pop_size
        self.__epoch = epoch
        self.__encoding = encoding
        self.__best = None


    @property
    def best_phenotype(self):
        '''The best chromosome.'''
        return self.__best.Phen[0] if self.__best else None


    @abstractmethod
    def init_problem(self) -> GeatpyProblem:
        '''Initialize problem in geatpy framework.'''


    @abstractmethod
    def decode(self, x:List[int]) -> JSSolution:
        '''Convert encode to JSSolution instance.

        Args:
            x (List[int]): encode scheme for GA.
        '''


    def check_better_solution(self, algorithm:ea.SoeaAlgorithm, pop:ea.Population):
        '''Update solution if better solution found.'''
        best = algorithm.BestIndi
        if self.solution is None or best.ObjV[0][0]<self.solution.makespan:
            s = self.decode(best.Phen[0])
            self.update_solution(s)


    def do_solve(self):
        # create geatpy problem to solve
        problem = self.init_problem()

        # algorithm
        algorithm = ea.soea_SEGA_templet(problem,
                ea.Population(Encoding=self.__encoding, NIND=self.__pop_size),
                MAXGEN=self.__epoch, # stop when reaching the max generation or max time
                MAXTIME=self.max_time,
                outFunc=self.check_better_solution,
                logTras=1,
                verbose=False,
                drawing=0)

        # solve
        self.__best, _pop = algorithm.run()
        solution = self.decode(self.best_phenotype)
        self.update_solution(solution)


class GAGeatpySolver(IGeatpySolver):
    '''General encode method for JSSP.'''

    def init_problem(self) -> None:
        dim = len(self.problem.ops)
        return GeatpyProblem(name=self.name,
                             var_type=1, # 0-continuous, 1-integer
                             dim=dim,
                             lb=[0]*dim,
                             ub=[dim-1]*dim,
                             solver=self)


    def decode(self, x:List[int]) -> JSSolution:
        '''Convert permutation code to JSSolution instance.

        Args:
            x (List[int]): permutation of operation index.
        '''
        solution = self.init_solution(direct_mode=False)

        # group operation with job id
        job_ops = defaultdict(list) # type: List[OperationStep]
        for op in solution.ops:
            job_ops[op.source.job.id].append(op)

        # convert operation sequence to job sequence to
        # avoid unavailable permutation
        ops = self.problem.ops
        job_sequence = [ops[i].job.id for i in x]

        # dispatch
        ops = [job_ops[i].pop(0) for i in job_sequence]
        solution.dispatch(ops=ops)
        return solution
