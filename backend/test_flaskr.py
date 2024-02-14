import os
from traceback import print_tb
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        # setup_db(self.app, self.database_path)

        # # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    @TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_categories(self):
        res = self.client().get('/categories')
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(len(body['categories']))

    # GET /questions

    def test_get_questions_200(self):
        res = self.client().get('/questions')
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])

    def test_get_questions_404(self):
        res = self.client().get('/questions?category=0')
        body = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(body['success'])

    # DELETE /questions/id

    def test_delete_questions_200(self):
        res = self.client().delete('/questions/12')
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertEqual(body['question_id'], 12)
        question = Question.query.get(12)
        self.assertEqual(question, None)

    def test_delete_questions_404(self):
        res = self.client().delete('/questions/3')
        body = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 404)
        self.assertEqual(body['message'], 'Not Found')

    # POST /questions

    def test_post_questions_201(self):
        res = self.client().post('/questions', json={
            'question': 'this is a question',
            'answer': 'this is an answer for the question',
            'category': 1,
            'difficulty': 2
        })
        body = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(body['success'])
        self.assertTrue(body['question_id'])

    def test_post_questions_400(self):
        res = self.client().post('/questions', json={
            'question': 'this is a question',
            'answer': 'this is an answer for the question',
            'category': 1,
        })
        body = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 400)
        self.assertEqual(body['message'], 'Bad Request')

    def test_post_questions_200(self):
        res = self.client().post('/questions', json={
            'searchTerm': 'What boxer\'s original name is Cassius Clay?'
        })
        body = res.get_json()
        print(body)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(len(body['questions']))
        self.assertTrue(body['total_questions'])

    def test_post_questions_404(self):
        res = self.client().post('/questions', json={
            'searchTerm': 'tasd is a question'
        })
        body = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 404)
        self.assertEqual(body['message'], 'Not Found')

    # GET /categories/<int:category_id>/questions

    def test_get_questions_by_cate_200(self):
        res = self.client().get('/categories/1/questions')
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['success'])
        self.assertTrue(body['questions'])
        self.assertTrue(body['current_category'])
        self.assertTrue(body['total_questions'])

    def test_get_questions_by_cate_404(self):
        res = self.client().get('/categories/0/questions')
        body = res.get_json()
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 404)
        self.assertEqual(body['message'], 'Not Found')

    # POST /quizzes

    def test_post_quizzes_200(self):
        res = self.client().post(
            '/quizzes', json={"previous_questions": "this is a question"})
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['question'])

    def test_post_quizzes_with_category_200(self):
        res = self.client().post('/quizzes',
                                 json={"previous_questions": "this is a question",
                                       "quiz_category": {"id": "0"}})
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(body['question'])

    def test_post_quizzes_400(self):
        res = self.client().post('/quizzes', json={})
        body = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], 400)
        self.assertEqual(body['message'], 'Bad Request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
