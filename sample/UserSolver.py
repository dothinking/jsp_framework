'''User solver sample.'''

import time
from jsp import (JSProblem, JSSolution, JSSolver)


class UserSolver(JSSolver):
    '''Sample solver.'''

    def do_solve(self, problem:JSProblem):
        '''A sample solving process: the sequence of operations assigned to each machine
        is determined by job id. Obviously, it's a feasible but far from optimal solution.
        '''
        # (1) Initialize an empty solution from problem
        solution = JSSolution(problem, direct_mode=False)

        # (2) Solve or optimize the solution, i.e., determine the start_time of
        # OperationStep instances. In this case, just sort operations by job id,
        # then create chain accordingly.
        ops = sorted(solution.ops, key=lambda op: op.source.job.id)
        for op in ops:
            solution.dispatch(op)

            # (3) Optional: update solution iteratively
            time.sleep(0.1)
            self.update_solution(solution)


if __name__=='__main__':

    p = JSProblem(benchmark='la01')

    s = UserSolver()
    s.solve(problem=p,
            interval=0,
            callback=lambda solution: print(f'makespan: {solution.makespan}'))

    s.wait()
    s.solution.plot_gantt_chart()
