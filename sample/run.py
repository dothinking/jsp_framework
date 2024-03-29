'''Test.'''

import logging
from jsp import (JSProblem, JSSolution)
from jsp.solver import (GoogleORCPSolver, PriorityDispatchSolver, PuLPSolver)


def print_intermediate_solution(solution:JSSolution):
    '''User callback function: print makespan.'''
    logging.info('Makespan: %f', solution.makespan)


if __name__=='__main__':

    # ----------------------------------------
    # create problem from benchmark
    # ----------------------------------------
    problem = JSProblem(benchmark='la01') #la01
    # problem = JSProblem(benchmark='ft10')
    # problem = JSProblem(input_file='1.txt')


    # ----------------------------------------
    # test built-in solver
    # ----------------------------------------
    # google or-tools
    s = GoogleORCPSolver(max_time=100)

    # priority dispatching
    rules = ['spt', 'mopr', 'mwkr', 'hh', 'ihh']
    # s = PriorityDispatchSolver(rule=rules[-2])

    # pulp solver
    s = PuLPSolver(max_time=300, solver_name='SCIP', msg=1)

    # ----------------------------------------
    # solve and result
    # ----------------------------------------
    s.solve(problem=problem, interval=2000, callback=print_intermediate_solution)
    s.wait()
    print('----------------------------------------')
    if s.status:
        print(f'Problem: {len(problem.jobs)} jobs, {len(problem.machines)} machines')
        # print(f'Optimum: {problem.optimum}')
        print(f'Solution: {s.solution.makespan}')
        print(f'Terminate successfully in {s.user_time} sec.')
    else:
        print(f'Solving process failed in {s.user_time} sec.')
