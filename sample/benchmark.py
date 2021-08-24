import logging
from jsp_fwk import (JSProblem, JSSolution, BenchMark)
from jsp_fwk.solver import (GoogleORCPSolver, PriorityDispatchSolver, PriorityDispatchProSolver)


def print_intermediate_solution(solution:JSSolution):
    logging.info(f'Makespan: {solution.makespan}')


if __name__=='__main__':

    # ----------------------------------------
    # create problem from benchmark
    # ----------------------------------------
    names = ['ft06', 'la01', 'ft10', 'swv01', 'la38', \
            'ta31', 'swv12', 'ta42', 'ta54', 'ta70']
    problems = [JSProblem(benchmark=name) for name in names]

    # ----------------------------------------
    # test built-in solver
    # ----------------------------------------
    # googl or-tools
    s = GoogleORCPSolver(max_time=300)

    # priority dispatching
    # s = PriorityDispatchSolver(rule='spt')
    # s = PriorityDispatchSolver(rule='mopr')
    # s = PriorityDispatchSolver(rule='mwkr')
    s1 = PriorityDispatchSolver(rule='t')

    solvers = [s,s1]

    # ----------------------------------------
    # solve and result
    # ----------------------------------------
    benchmark = BenchMark(problems=problems, solvers=solvers, num_threads=6)
    benchmark.run(show_info=True, callback=print_intermediate_solution)