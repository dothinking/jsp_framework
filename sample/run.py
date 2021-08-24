import logging
from jsp_fwk import (JSProblem, JSSolution)
from jsp_fwk.solver import (GoogleORCPSolver, PriorityDispatchSolver, PriorityDispatchProSolver)


def print_intermediate_solution(solution:JSSolution):
    logging.info(f'Makespan: {solution.makespan}')


if __name__=='__main__':

    # ----------------------------------------
    # create problem from benchmark
    # ----------------------------------------
    problem = JSProblem(benchmark='ft06')

    # ----------------------------------------
    # test built-in solver
    # ----------------------------------------
    # googl or-tools
    # s = GoogleORCPSolver()

    # priority dispatching
    # s = PriorityDispatchSolver(rule='spt')
    # s = PriorityDispatchSolver(rule='mopr')
    # s = PriorityDispatchSolver(rule='mwkr')
    # s = PriorityDispatchSolver(rule='t')
    s = PriorityDispatchSolver(rule='c')

    # ----------------------------------------
    # solve and result
    # ----------------------------------------
    s.solve(problem=problem, interval=2000, callback=print_intermediate_solution)
    s.wait()
    print('----------------------------------------')
    if s.status:
        print(f'Problem: {len(problem.jobs)} jobs, {len(problem.machines)} machines')
        print(f'Optimum: {problem.optimum}')
        print(f'Solution: {problem.solution.makespan}')
        print(f'Terminate successfully in {s.user_time} sec.')
    else:
        print(f'Solving process failed in {s.user_time} sec.')