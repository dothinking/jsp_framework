from model.problem import JSProblem
from solver.SampleSolver import SampleSolver


if __name__=='__main__':

    problem = JSProblem(benchmark='ft06')

    s = SampleSolver(name='sample')
    s.solve(problem=problem)