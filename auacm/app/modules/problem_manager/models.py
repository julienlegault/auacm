'''Provide model objects for representing problems.'''
from app.database import Base, session

# Problem = Base.classes.problems

class Problem(Base):
    '''Problem class that we build by reflecting the mysql database.'''

    __tablename__ = "problems"

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)


class  Problem_Data(Base):
    '''Problem Data class that reflects mysql database'''

    __tablename__ = 'problem_data'

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)

class Sample_Case(Base):
    '''Test case class that reflects the mysql database'''

    __tablename__ = 'sample_cases'

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
