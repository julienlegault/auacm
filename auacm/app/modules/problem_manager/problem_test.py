"""Tests for problem CRUD-ing

To run these tests, execute the following at the app level:

<code>
./test.py
</code>

These tests assume that the login functionality works, and depends on having
access to the test database.

Interesting fact, Benjamin Franklin was the oldest signer of the Declaration
of Independence at 70 years old.
"""

import unittest
import json

from app import app, test_app
from models import Problem, ProblemData, SampleCase
from app.database import test_session

# TODO: Test get_problem (detailed info)
# TODO: Test create_problem (and all of its subtests)
# TODO: Test delete_problem
# TODO: Test updating a problem

# Test data to work with
test_problem = {
    'pid': 9999,
    'name': 'This is a test',
    'shortname': 'thisisatest',
    'appeared': 'Not a real Competition',
    'difficulty': 100,
    'added': 1,
    'comp_release': 1
}
test_problem_data = {
    'pid': 9999,
    'description': 'This is a test problem. There is no need for alarm.',
    'input_desc': 'Some values and stuff',
    'output_desc': 'Other things. Like the right answer.',
    'time_limit': 90
}
test_cases = [{
    'pid': 9999,
    'case_num': 1,
    'input': '1 1',
    'output': '2'
}, {
    'pid': 9999,
    'case_num': 2,
    'input': '2 2',
    'output': '4'
}]


# Helper methods to log in/out of the web app (tests assume they work)
def _login():
    username = app.config['TEST_USERNAME']
    password = app.config['TEST_PASSWORD']
    rv = json.loads(test_app.post(
        '/api/login',
        data=dict(username=username, password=password)).data)
    assert 200 == rv['status']

def _logout():
    rv = json.loads(test_app.get('/api/logout').data)
    assert 200 == rv['status']


class ProblemGetTests(unittest.TestCase):
    """Tests functionality for GET-ing problems from the API"""

    def setUp(self):
        """Manually add a problem to the test database"""
        self.p = Problem(**test_problem)
        self.pd = ProblemData(**test_problem_data)
        self.cases = list()
        for c in test_cases:
            self.cases.append(SampleCase(**c))

        # Ship it off to the db
        test_session.add(self.p)
        test_session.add(self.pd)
        for c in self.cases: test_session.add(c)
        test_session.commit()

        # Log in
        _login()

    def testGetAll(self):
        """Should get basic info about all the problems"""
        rv = json.loads(test_app.get('/api/problems').data)
        self.assertEqual(200, rv['status'])
        self.assertFalse('Please log in' in str(rv))

        found = None
        for prob in rv['data']:
            if prob['pid'] == test_problem['pid']:
                found = prob

        self.assertTrue(len(rv['data']) > 0)
        self.assertFalse(found is None)

        # All the original values should be maintained
        for k in test_problem:
            self.assertEqual(str(test_problem[k]), str(found[k]))

    def tearDown(self):
        """Manually remove test problem from the test database"""
        for c in self.cases:
            test_session.delete(c)
        test_session.delete(self.pd)
        test_session.delete(self.p)
        test_session.commit()

        # Log out of this session too
        _logout()


if __name__ == '__main__':
    unittest.main()
