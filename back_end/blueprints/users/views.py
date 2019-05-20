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
from playhouse.shortcuts import model_to_dict


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
					qid = elem["PrimaryAttribute"]
					question_id = re.sub(r"\D", "", qid)
					# breakpoint()
					question_type = elem["Payload"]["QuestionType"]
					q_text = elem["Payload"]["QuestionText"]
					question_text = re.sub(r"<[a-zA-Z\/][^>]*>", "", q_text)
					new_question = Question(survey_id=survey_id, question_id=question_id, question_type=question_type,
											question_text=question_text, search_content=fn.to_tsvector(question_text))
					# try and save the question, if got duplication do nothing.
					# new_question.save()
					try:
						new_question.save()
					except:
						pass
					# if answers are available, loop through the answers to extract data:
					if "Choices" in elem["Payload"]:
						answers = elem["Payload"]["Choices"]
						for index, answer in answers.items():
							content = answer["Display"]
							new_qna = QuestionAnswer(
								question_id=question_id, choices_index=int(index), choices_text=content, search_content=fn.to_tsvector(content))
							# new_qna.save()
							try:
								new_qna.save()
							except:
								# pass if duplicate
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

# https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041
def convert_to_dict(obj):
  """
  A function takes in a custom object and returns a dictionary representation of the object.
  This dict representation includes meta data such as the object's module and class names.
  """
  #  Populate the dictionary with object meta data 
  obj_dict = {
	"__class__": obj.__class__.__name__,
	"__module__": obj.__module__
  }
  
  #  Populate the dictionary with object properties
  obj_dict.update(obj.__dict__)
  
  return obj_dict

# get top 10 latest questions saved
@users_api_blueprint.route('/read', methods=['GET'])
def read():
	question_results = Question.select().order_by(Question.updated_at).limit(10)
	# answer_results = QuestionAnswer.select().where(QuestionAnswer.question_id == qresult.question_id).order_by(QuestionAnswer.updated_at).limit(10)

	get_data = []
	for qresult in question_results:
		question_data = {"question_id": qresult.question_id,
					"question_type": qresult.question_type,
					"question_text": qresult.question_text}
		answer_results = QuestionAnswer.select().join(Question, on =(QuestionAnswer.question_id == Question.question_id)).where(QuestionAnswer.question_id==qresult.question_id)
		# store the answers for a particular question in an array
		ans_list = []
		for aresult in answer_results:
			ans= {"question_id":aresult.question_id,
			"choices_index": aresult.choices_index,
			"choices_text": aresult.choices_text}
			ans_list.append(ans)
		question_data.update({"answer":ans_list})
		get_data.append(question_data)
	return json.dumps(get_data)
	# return json.dumps(model_to_dict(get_data))
	# return json.dumps(get_data, default=convert_to_dict) #circular reference error
	# return json.dumps(get_data) #TypeError: Object of type QuestionAnswer is not JSON serializable
	# return jsonify(get_data) #TypeError: Object of type QuestionAnswer is not JSON serializable

# get only the search result
@users_api_blueprint.route('/search/<search_term>', methods=['GET'])
def search(search_term):
	question_results = Question.select().where(Question.search_content.match(search_term))
	searched_data =[]
	for qresult in question_results:
		question_data = {"question_id": qresult.question_id,
					  "question_type": qresult.question_type,
					  "question_text": qresult.question_text}
		answer_results = QuestionAnswer.select().join(Question, on =(QuestionAnswer.question_id == Question.question_id)).where(QuestionAnswer.question_id==qresult.question_id)
		ans_list = []
		# store the answers for a particular question in an array
		for aresult in answer_results:
			ans= {"question_id":aresult.question_id,
			"choices_index": aresult.choices_index,
			"choices_text": aresult.choices_text}
			ans_list.append(ans)
		question_data.update({"answer":ans_list})
		searched_data.append(question_data)
	return json.dumps(searched_data)
	# return jsonify(searched_data)
 