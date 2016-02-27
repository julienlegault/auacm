#!flask/bin/python
from app import database
from app.modules.problem_manager.models import ProblemData
from app.modules.problem_manager import problem_timer


def time_problems():
    problems = database.session.query(ProblemData).all()
    for problem in problems:
        problem_timer.Timer(problem).run()


if __name__ == '__main__':
    time_problems()
