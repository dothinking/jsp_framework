'''Hybrid methods, e.g., GA and priority dispatching.'''
from typing import List
from ..model.variable import OperationStep
from ..model.problem import JSProblem
from ..model.solution import JSSolution
from .ga import (IGeatpySolver, GeatpyProblem)
from .dp import (DisPatchingRules, PriorityDispatchSolver)


class GADPGeatpySolver(IGeatpySolver):
    '''GA + DP method for JSSP.'''

    def __init__(self,
                 name:str=None,
                 problem:JSProblem=None,
                 pop_size:int=32,
                 epoch:int=None,
                 max_time:int=None) -> None:
        super().__init__(name, problem, 'RI', pop_size, epoch, max_time) # real/integer encoding


    def init_problem(self):
        dim = 2
        return GeatpyProblem(name=self.name,
                             var_type=0,
                             dim=dim,
                             lb=[-2]*dim,
                             ub=[2]*dim,
                             solver=self)


    @staticmethod
    def fun_rule(x:List[int], op:OperationStep, solution:JSSolution):
        '''Combined rule based on basic rules.'''
        remaining = DisPatchingRules.TWR(op, solution) - 1.5*DisPatchingRules.PT(op, solution)
        return DisPatchingRules.EST(op, solution) + \
            DisPatchingRules.PT(op, solution) * x[0] + \
            DisPatchingRules.WT(op, solution) * x[1], -remaining


    def decode(self, x:List[int]) -> JSSolution:
        '''Convert permutation code to JSSolution instance.

        Args:
            x (List[int]): permutation of operation index.
        '''
        def fun(op, sol): return self.fun_rule(x, op, sol)
        s = PriorityDispatchSolver(problem=self.problem, rule=fun)
        s.solve()
        s.wait()
        return s.solution
