from http.client import HTTPException
import os
from unicodedata import category
from wsgiref import headers
from click import Abort
from flask import Flask, Request, Response, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

import werkzeug

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_qustions(req: Request, questions: Question):
    page = req.args.get('page', 1, int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatedQuest = [q.format() for q in questions]
    selectedQuest = formatedQuest[start:end]
    return selectedQuest


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, origins='*')

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response: Response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def getCategories():
        try:
            categories = Category.query.order_by(Category.id).all()
            if categories is None:
                abort(404)
            else:
                return jsonify(
                    {
                        'success': True,
                        'categories': [c.type for c in categories]
                    }
                ), 200
        except:
            abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def getQuestions():
        try:
            cate = request.args.get('category', 1, type=int)
            if cate is None:
                tempQuest = Question.query.all()
            else:
                tempQuest = Question.query.filter_by(category=cate).all()
            selectedQuest = paginate_qustions(request, tempQuest)
            if len(selectedQuest) == 0:
                abort(404)
            else:
                return jsonify(
                    {
                        'success': True,
                        'questions': selectedQuest,
                        'total_questions': len(tempQuest),
                        'current_category': Category.query.get(cate).type,
                        'categories': [c.type for c in Category.query.all()]
                    }
                ), 200
        except werkzeug.exceptions.NotFound as he:
            print(he)
            abort(404)
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:quet_id>', methods=['DELETE'])
    def delQuestion(quet_id):
        try:
            deletedQuestion: Question = Question.query.get(quet_id)
            deletedQuestion.delete()
            return jsonify({
                'success': True,
                'question_id': deletedQuestion.id
            })
        except Exception as e:
            print(e)
            abort(500)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def addQuestion():
        body = request.get_json()
        if 'question' in body and body['question'] != '' and 'answer' in body and body['answer'] != '' and 'difficulty' in body and body['difficulty'] != '' and 'category' in body and body['category'] != '':
            print(body['category'])
            try:
                newQuest = Question(
                    body['question'], body['answer'], body['category'], body['difficulty'])
                newQuest.insert()
                return jsonify({
                    'success': True,
                    'question_id': newQuest.id
                }), 201
            except:
                abort(500)
        elif 'searchTerm' in body and body['searchTerm'] != '':
            try:
                formatedTerm = '%{}%'.format(body['searchTerm'])
                searchedQuestions = Question.query.filter(
                    Question.question.like(formatedTerm)).all()
                if len(searchedQuestions) == 0:
                    return abort(404)
                else:
                    return jsonify({
                        'success': True,
                        'questions': [q.format() for q in searchedQuestions],
                        'total_questions': len(searchedQuestions)
                    }), 200

            except werkzeug.exceptions.NotFound as he:
                print(he)
                abort(404)
            except:
                abort(500)
        else:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def getQuestByCate(category_id):
        selectedQuest = []
        cate = ''
        try:
            questions = Question.query.filter_by(category=category_id).all()
            selectedQuest = paginate_qustions(request, questions)
            cate = Category.query.get(category_id).type
        except:
            abort(500)
        if len(selectedQuest) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': selectedQuest,
                'total_questions': len(questions),
                'current_category': cate
            }), 200

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def getNextQuestion():
        try:
            body = request.get_json()
            if 'previous_questions' in body and body['previous_questions'] != '':
                if 'quiz_category' in body and body['quiz_category'] != '':
                    print(int(body['quiz_category']['id']) + 1)
                    nextQuest: Question = random.choice(Question.query.filter_by(
                        category=int(body['quiz_category']['id']) + 1).filter(
                        Question.question.not_like(body['previous_questions'])).all())
                    return jsonify({
                        'question': nextQuest.format()
                    }), 200
                else:
                    nextQuest: Question = random.choice(Question.query.filter(
                        Question.question.not_like(body['previous_questions'])).all())
                    return jsonify({
                        'question': nextQuest.format()
                    }), 200
            else:
                abort(400)
        except werkzeug.exceptions.BadRequest as he:
            print(he)
            abort(400)
        except Exception as e:
            print(e)
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify(
            {
                "success": False, "error": 422, "message": "Unprocessable"
            }
        ), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "success": False, "error": 404, "message": "Not Found"
            }
        ), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                "success": False, "error": 400, "message": "Bad Request"
            }
        ), 400

    @app.errorhandler(500)
    def not_found(error):
        return jsonify(
            {
                "success": False, "error": 500, "message": "Internal Server Error"
            }
        ), 500

    return app
