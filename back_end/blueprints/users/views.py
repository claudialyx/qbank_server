from flask import Blueprint, make_response, jsonify, request
from werkzeug.utils import secure_filename
import os
from app import app
import json
import re
from models.question import *
from models.questionAnswer import *
from peewee import fn
from playhouse.postgres_ext import Match


users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')

# UPLOAD_FOLDER = '/path/to/the/uploads'
UPLOAD_FOLDER = 'C:\\Users\\User\\Desktop\\Project\\qbank_interview\\qbank_server'
ALLOWED_EXTENSIONS = set(['qsf'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def text_search(search_term):
    return Question.select() & Match(Question.question_text, search_term)


@users_api_blueprint.route('/', methods=['GET'])
def index():
    return "USERS API"


# def checkAnswerExist(answers, question_id):
#     for answer in answers:
#         for ans in answer:
#             for display in ans:
#                 new_qna = QuestionAnswer(
#                     question_id=question_id, choices=display)
#                 breakpoint()
#                 # if new_qna.save():
#                 try:
#                     new_qna.save()
#                 except:
#                     pass
#                 responseObject1 = {
#                     'status': 'Success',
#                     'message': 'Successfully saved in database'
#                 }
#                 return responseObject1


@users_api_blueprint.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    # if file and allowed file type is correct
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # save file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # open file to extract data to save in database
        with open(filename, 'r') as f:
            file_content = json.load(f)
            survey_id = file_content["SurveyEntry"]["SurveyID"]
            survey_name = file_content["SurveyEntry"]["SurveyName"]
            survey_elements = file_content["SurveyElements"]
            # to loop through SQ type element
            for elem in survey_elements:
                if elem["Element"] == "SQ":
                    question_id = elem["PrimaryAttribute"]
                    question_type = elem["Payload"]["QuestionType"]
                    q_text = elem["Payload"]["QuestionText"]
                    question_text = re.sub(r"<[a-zA-Z\/][^>]*>", "", q_text)
                    # if answers are available:
                    # breakpoint()
                    if "Choices" in elem["Payload"]:
                        answers = elem["Payload"]["Choices"]
                        # checkAnswerExist(answers, question_id)
                        for index, answer in answers.items():
                            content = answer["Display"]
                            new_qna = QuestionAnswer(
                                question_id=question_id, choices_index=int(index), choices_text=content)
                            breakpoint()
                            new_qna.save()
                            # try:
                            #     new_qna.save()
                            # except:
                            #     print("not saved")
                    new_question = Question(survey_id=survey_id, question_id=question_id, question_type=question_type,
                                            question_text=question_text, search_content=fn.to_tsvector(question_text))
                    # if new_question.save() and new_qna.save():
                    # breakpoint()
                    # try and save the question, if got duplication do nothing.
                    try:
                        new_question.save()
                    except:
                        pass
                    responseObject = {
                        'status': 'Success',
                        'message': 'Successfully saved in database'
                    }
        return make_response(jsonify(responseObject)), 201

    # if allowed_file(file.filename) == False:
    responseObject = {
        'status': 'Failed',
        'message': 'Invalid file type. Not saved in database. Please ensure file ext ends with .qsf'
    }
    return make_response(jsonify(responseObject)), 200

# get top 10 latest questions saved
@users_api_blueprint.route('/read', methods=['GET'])
def read():
    results = Question.select().order_by(Question.updated_at).limit(10)
    get_data = [{"question_id": result.question_id,
                 "question_type": result.question_type,
                 "question_text": result.question_text} for result in results]
    return jsonify(get_data)

# get only the search result
@users_api_blueprint.route('/search/<search_term>', methods=['GET'])
def search(search_term):
    results = Question.select().where(Question.search_content.match(search_term))
    searched_data = [{"question_id": result.question_id,
                      "question_type": result.question_type,
                      "question_text": result.question_text} for result in results]
    return jsonify(searched_data)
