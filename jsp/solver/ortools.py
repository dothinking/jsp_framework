'''Google OR-Tools solver.'''
from collections import (namedtuple, defaultdict)
from ortools.sat.python import cp_model
from ..common.exception import JSPException
from ..model.solver import JSSolver
from ..model.solution import JSSolution


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    '''Output intermediate solutions.

    https://github.com/google/or-tools/blob/stable/ortools/sat/doc/solver.md#printing-intermediate-solutions
    '''
    def __init__(self, variables:dict, solver:JSSolver, solution:JSSolution):
        '''Initialize with variable map: operation step -> OR-Tools variable.'''
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solver = solver
        self.__solution = solution

    def on_solution_callback(self):
        '''Pass data back to domain class.'''
        # assign OR-Tools solution back to JSPSolution
        for op, var in self.__variables.items():
            op.update_start_time(self.Value(var.start))

        # update solution
        self.__solver.update_solution(self.__solution)


class GoogleORCPSolver(JSSolver):
    '''Google OR-Tools solver.'''


    def do_solve(self):
        '''Solve JSP with Google OR-Tools.

        https://developers.google.cn/optimization/scheduling/job_shop
        '''
        # Initialize an empty solution from problem
        solution = self.init_solution(direct_mode=True)

        # create model
        model, variables = self.__create_model(solution)

        # set solver
        solver = cp_model.CpSolver()
        if self.max_time is not None:
            solver.parameters.max_time_in_seconds = self.max_time # set time limit

        solution_printer = VarArraySolutionPrinter(variables, self, solution)
        status = solver.SolveWithSolutionCallback(model, solution_printer)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
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
            i,j = source.job.id, source.machine.id
            start_var = model.NewIntVar(0, max_time, f'start-{i}-{j}')
            end_var = model.NewIntVar(0, max_time, f'end-{i}-{j}')
            interval_var = model.NewIntervalVar(start_var,
                                                source.duration,
                                                end_var,
                                                f'interval-{i}-{j}')
            variables[op] = variable(start=start_var, end=end_var, interval=interval_var)
            machine_intervals[source.machine].append(interval_var)

        # apply constraints
        # (1) no overlap for operations assigned to same machine
        for interval_vars in machine_intervals.values():
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
        model.AddMaxEquality(obj_var,
                             [variables[job.tail_job_op].end for job in solution.job_ops])
        model.Minimize(obj_var)

        return model, variables
