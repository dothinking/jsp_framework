from collections import (namedtuple, defaultdict)
from ortools.sat.python import cp_model
from ..common.exception import JSPException
from ..model.solver import JSSolver
from ..model.problem import JSProblem
from ..model.solution import JSSolution


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    '''Output intermediate solutions.

    https://github.com/google/or-tools/blob/stable/ortools/sat/doc/solver.md#printing-intermediate-solutions
    '''
    def __init__(self, variables:dict, problem:JSProblem, solution:JSSolution):
        '''Initialize with variable map: operation step -> OR-Tools variable.'''
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__problem = problem
        self.__solution = solution

    def on_solution_callback(self):
        '''Pass data back to domain class.'''
        # assign OR-Tools solution back to JSPSolution
        for op, var in self.__variables.items():
            op.start_time = self.Value(var.start)
        
        # update solution
        self.__problem.update_solution(self.__solution)



class GoogleORCPSolver(JSSolver):

    def do_solve(self, problem:JSProblem):
        '''Solve JSP with Google OR-Tools.

        https://developers.google.cn/optimization/scheduling/job_shop
        '''
        # Initialize an empty solution from problem
        solution = JSSolution(problem)
       
        # Solving with Google OR-Tools
        model, variables = self.__create_model(solution)
        solver = cp_model.CpSolver()
        # status = solver.Solve(model)

        solution_printer = VarArraySolutionPrinter(variables, problem, solution)
        status = solver.SolveWithSolutionCallback(model, solution_printer)

        if status!=cp_model.OPTIMAL and status!=cp_model.FEASIBLE:
            raise JSPException('No feasible solution found.')
    


    def __create_model(self, solution:JSSolution):
        '''Create Google OR-Tools model: variables, constraints and objective.'''
        # create the model: constraint programming
        model = cp_model.CpModel()

        # create variables
        variable = namedtuple('variable', 'start, end, interval') # variable for a single operation        
        max_time = sum(op.source.duration for op in solution.ops) # upper bound of variables

        variables = {} # all variables
        machine_intervals = defaultdict(list) # interval variables assigned to same machine
        for op in solution.ops:
            source = op.source
            i = source.id
            start_var = model.NewIntVar(0, max_time, f'start-{i}')
            end_var = model.NewIntVar(0, max_time, f'end-{i}')
            interval_var = model.NewIntervalVar(start_var, source.duration, end_var, f'interval-{i}')
            variables[op] = variable(start=start_var, end=end_var, interval=interval_var)
            machine_intervals[source.machine].append(interval_var)
        
        # apply constraints
        # (1) no overlap for operations assigned to same machine
        for machine, interval_vars in machine_intervals.items():
            model.AddNoOverlap(interval_vars)
        
        # (2) operation sequence inside a job
        pre = None
        for op, var in variables.items():
            if pre and pre.source.job==op.source.job:
                pre_var = variables[pre]
                model.Add(pre_var.end<=var.start)
            pre = op
        
        # objective: makespan
        obj_var = model.NewIntVar(0, max_time, 'makespan')
        model.AddMaxEquality(obj_var, [variables[ops[-1]].end for job, ops in solution.job_ops.items()])
        model.Minimize(obj_var)

        return model, variables