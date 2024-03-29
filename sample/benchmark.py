'''Solvers benchmark.'''
import logging
from jsp import (JSProblem, JSSolution, BenchMark)
from jsp.solver import (GoogleORCPSolver, PriorityDispatchSolver, PuLPSolver)


def print_intermediate_solution(solution:JSSolution):
    '''User callback.'''
    logging.info('Makespan: %f', solution.makespan)


if __name__=='__main__':

    # ----------------------------------------
    # create problem from benchmark
    # ----------------------------------------
    names = ['ft06', 'la01', 'ft10', 'swv01', 'la38', 'ta24', 'ta31', 'swv12', 'ta24', 'ta42', 'ta54', 'ta68', 'ta69', 'ta70']
    # names = ['ft06', 'la01']
    names = ['ft06', 'la01', 'ft10', 'swv01', 'la38']
    problems = [JSProblem(benchmark=name) for name in names]

    # ----------------------------------------
    # test built-in solver
    # ----------------------------------------
     # googl or-tools
    s1 = GoogleORCPSolver(max_time=300)

    # priority dispatching
    s2 = PriorityDispatchSolver(rule='hh')

    # PuLP solver
    s3 = PuLPSolver(solver_name='SCIP', max_time=300)

    # ----------------------------------------
    # solve and result
    # ----------------------------------------
    benchmark = BenchMark(problems=problems, solvers=[s2,s3], num_threads=6)
    benchmark.run(show_info=True)
