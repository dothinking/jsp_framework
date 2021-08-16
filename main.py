from model.problem import JSProblem
from model.solver import JSSolver



if __name__=='__main__':

    problem = JSProblem(benchmark='ft06')

    s = JSSolver(name='default')

    s.solve(problem=problem)

    print('done...')