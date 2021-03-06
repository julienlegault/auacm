"""Tests for problem CRUD-ing

To run these tests, execute the following at the app level:

<code>
./test.py problem
</code>

These tests assume that the login functionality works, and depends on having
access to the test database.

Interesting fact, Benjamin Franklin was the oldest signer of the Declaration
of Independence at 70 years old.
"""

import unittest
import json
import copy
from time import time

from app import app, test_app
from app.modules.problem_manager.models import Problem, ProblemData, SampleCase
from app.modules.competition_manager.models import Competition
from app.util import AUACMTest
from pymysql.err import IntegrityError
import app.database as database

session = database.session


# TODO: Test invalid requests to problem(s)
# TODO: Problem subtests (different arguments, etc)

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


def _reinsert_test_problem(test_prob, test_prob_data, test_cases):
    # Find the problem
    cases = session.query(SampleCase).\
        filter(SampleCase.pid == test_problem['pid']).all()
    data = session.query(ProblemData).\
        filter(ProblemData.pid == test_problem['pid']).first()
    problem = session.query(Problem).\
        filter(Problem.pid == test_problem['pid']).first()

    # Remove it (if it was actually in there)
    for case in cases:
        session.delete(case)
    if data: session.delete(data)
    if problem: session.delete(problem)
    session.commit()

    # Put in the fresh test problem
    session.add(test_prob)
    session.add(test_prob_data)
    for c in test_cases:
        session.add(c)
    session.commit()

class ProblemGetTests(AUACMTest):
    """Tests functionality for GET-ing problems from the API"""

    def setUp(self):
        """Manually add a problem to the test database"""
        self.p = Problem(**test_problem)
        self.pd = ProblemData(**test_problem_data)
        self.cases = list()
        for c in test_cases:
            self.cases.append(SampleCase(**c))

        # Ship it off to the db
        try:
            session.add(self.p)
            session.add(self.pd)
            for c in self.cases: session.add(c)
            session.commit()
        except:
            session.rollback()
            _reinsert_test_problem(self.p, self.pd, self.cases)

        # Log in
        self.login()

    def tearDown(self):
        """Manually remove test problem from the test database"""
        for c in self.cases:
            session.delete(c)
        session.delete(self.pd)
        session.delete(self.p)
        session.commit()

        # Log out of this session too
        self.logout()

    def testGetAll(self):
        """Should get basic info about all the problems"""
        # Check that the request went through
        resp = test_app.get('/api/problems')
        self.assertEqual(200, resp.status_code)
        rv = json.loads(resp.data.decode())
        self.assertFalse('Please log in' in str(rv))

        # Find the test problem in the list returned
        found = None
        for prob in rv['data']:
            if prob['pid'] == test_problem['pid']:
                found = prob

        self.assertTrue(len(rv['data']) > 0)
        self.assertFalse(found is None)

        # All the original values should be maintained
        for k in test_problem:
            self.assertEqual(str(test_problem[k]), str(found[k]))

    def testGetOne(self):
        """Should get detailed info about one specific problem"""
        resp = test_app.get('/api/problems/' + str(test_problem['pid']))
        self.assertEqual(200, resp.status_code)

        rv = json.loads(resp.data.decode())
        self.assertFalse('Please log in' in str(rv))

        # Time limit doesn't get returned from the API, so take it out of our
        # validation
        data_validate = copy.deepcopy(test_problem_data)
        data_validate.pop('time_limit')

        prob = rv['data']
        for key in test_problem:
            self.assertEqual(str(test_problem[key]), str(prob[key]))
        for key in data_validate:
            self.assertEqual(str(test_problem_data[key]), str(prob[key]))

    def testHideUnreleasedProblem(self):
        """Test that GET-ting an unreleased problem returns a 404"""
        unreleased_cid = self._setUpUnreleasedComp()

        resp = test_app.get('/api/problems/{}'.format(self.p.pid))
        self.assertEqual(404, resp.status_code)

        self._tearDownComp(unreleased_cid)

    def testHideUnreleasedProblems(self):
        """
        Test that GET-ting all problems doesn't return unreleased problems
        """
        unreleased_cid = self._setUpUnreleasedComp()

        resp = test_app.get('/api/problems')
        self.assertEqual(200, resp.status_code)
        rv = json.loads(resp.data.decode())['data']

        # Test problem should be hidden
        for prob in rv:
            self.assertNotEqual(self.p.pid, prob['pid'])

        self._tearDownComp(unreleased_cid)

    def _setUpUnreleasedComp(self):
        """
        Creates an unreleased competition and associates the test's problem with it

        :return: the cid of the new competition
        """
        unreleased_cid = Competition(
            name='Test Competition',
            start=int(time() + 10000),
            stop=int(time() + 20000),
            closed=0
        ).commit_to_session(session)

        self.p.comp_release = unreleased_cid
        self.p.commit_to_session(session)

        return unreleased_cid

    def _tearDownComp(self, cid):
        """Removes a competition from the database by its cid"""
        session.delete(
            session.query(Competition)
            .filter_by(cid=cid)
            .first()
        )
        session.commit()


class ProblemEditTests(AUACMTest):
    """Tests functionality for editing an existing problem"""

    def setUp(self):
        """Prepare test database for tests"""
        self.p = Problem(**test_problem)
        self.pd = ProblemData(**test_problem_data)
        self.cases = list()
        for c in test_cases:
            self.cases.append(SampleCase(**c))

        # Ship it off to the db
        try:
            session.add(self.p)
            session.add(self.pd)
            for c in self.cases: session.add(c)
            session.commit()
        except:
            session.rollback()
            _reinsert_test_problem(self.p, self.pd, self.cases)

        # Log in
        self.login()

    def testProblemEdit(self):
        new_name = 'A Different Test Problem'
        resp = test_app.put(
            '/api/problems/' + str(test_problem['pid']),
            data={'name':new_name})
        self.assertEqual(200, resp.status_code)

        rv = json.loads(resp.data.decode())
        prob = rv['data']
        self.assertEqual(new_name, prob['name'])

    def tearDown(self):
        """Tie up loose ends from test"""
        for c in self.cases:
            session.delete(c)
        session.delete(self.pd)
        session.delete(self.p)
        session.commit()

        # Log out of this session too
        self.logout()


class ProblemDeleteTests(AUACMTest):
    """Tests deleting a problem via the API"""

    def setUp(self):
        """Add the problem to be deleted to the database"""
        self.p = Problem(**test_problem)
        session.add(self.p)
        self.pd = ProblemData(**test_problem_data)
        session.add(self.pd)
        self.cases = list()
        for c in test_cases:
            self.cases.append(SampleCase(**c))
            session.add(self.cases[len(self.cases)-1])

        try:
            session.commit()
        except:
            session.rollback()
            _reinsert_test_problem(self.p, self.pd, self.cases)

        # Log in as well
        self.login()

    def testDeleteProblem(self):
        resp = test_app.delete('api/problems/' + str(test_problem['pid']))
        self.assertEqual(200, resp.status_code)
        rv = json.loads(resp.data.decode())
        self.assertEqual(str(test_problem['pid']), (rv['data']['deleted_pid']))

        # Ensure problem was removed from the database
        prob = session.query(Problem).\
            filter(Problem.pid == test_problem['pid']).first()
        self.assertIsNone(prob)

    def tearDown(self):
        """Delete the test problem only if unsuccessful"""
        prob = session.query(Problem).\
            filter(Problem.pid == test_problem['pid']).first()
        if prob is not None:
            prob_data = session.query(ProblemData).\
                filter(ProblemData.pid == test_problem['pid']).first()
            cases = session.query(SampleCase).\
                filter(SampleCase.pid == test_problem['pid']).all()
            session.delete(prob_data)
            for c in cases: session.delete(c)
            session.delete(prob)
            session.commit()

        # Log out as well
        self.logout()


if __name__ == '__main__':
    unittest.main()
