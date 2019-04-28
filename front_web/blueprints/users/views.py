from flask import Blueprint, render_template, request, redirect, flash, url_for
from app import app
import os
from werkzeug.utils import secure_filename
import json
from models.base_model import *
from models.question import *
from models.questionAnswer import *
import re

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


ALLOWED_EXTENSIONS = set(['txt', 'qsf'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')

@users_blueprint.route('/search', methods=['GET'])
def search():
    return render_template('users/search.html')

@users_blueprint.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        # if 'qsf_file' not in request.files:
        #     flash('No file part')
        #     return redirect(url_for('users.new'))
        
        file = request.files['qsf_file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(url_for('users.new'))
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(filename, 'r') as f:  
                file_content = json.load(f)
                survey_id = file_content["SurveyEntry"]["SurveyID"]
                survey_name = file_content["SurveyEntry"]["SurveyName"]
                survey_elements = file_content["SurveyElements"]
                for elem in survey_elements:
                    if elem["Element"] == "SQ":
                        question_id = elem["PrimaryAttribute"]
                        question_type = elem["Payload"]["QuestionType"]
                        q_text = elem["Payload"]["QuestionText"]
                        question_text = re.sub(r"<[a-zA-Z\/][^>]*>", "", q_text)
                        # q_text2 = re.sub(r"")
                        breakpoint()
                        # question_answers = {}
                        if "Choices" in elem["Payload"]:
                            answers = elem["Payload"]["Choices"]
                            for answer in answers:
                                for ans in answer:
                                    for display in ans:
                                        #cannot append answer, need to create a new model for choices
                                        new_qna = QuestionAnswer(question_id=question_id, choices=display)
                        new_question = Question(survey_id=survey_id, question_id=question_id, question_type=question_type,question_text=question_text)
                        if new_question.save():
                            flash('File(s) successfully uploaded')
                return redirect('/users/new')
    else:
        return render_template('users/new.html')


# @users_blueprint.route('/<username>', methods=["GET"])
# def show(username):
#     pass


# @users_blueprint.route('/', methods=["GET"])
# def index():
#     return "USERS"


# @users_blueprint.route('/<id>/edit', methods=['GET'])
# def edit(id):
#     pass


# @users_blueprint.route('/<id>', methods=['POST'])
# def update(id):
#     pass


# @users_blueprint.route("/new/upload", methods=["POST"])
# def upload_file():
# 	# A
#     if "user_file" not in request.files and "image_file" not in request.files:
#         return "No file in request.files"

# 	# B If the key is in the object, we save it in a variable called file.
#     if "user_file" in request.files:
#         file = request.files["user_file"]
#     if "image_file" in request.files:
#         file = request.files["image_file"]
#     """
#         These attributes are also available
#         file.filename               # The actual name of the file
#         file.content_type
#         file.content_length
#         file.mimetype
#     """
# 	# C. We check the filename attribute on the object and if it’s empty, 
#     # it means the user sumbmitted an empty form, so we return an error message.
#     if file.filename == "":
#         return "Please select a file"

# 	# D. we check that there is a file and that it has an allowed filetype
#     if file and allowed_file(file.filename):
#         file.filename = secure_filename(file.filename)
#         output = upload_file_to_s3(file, app.config['S3_BUCKET'])
#         if "user_file" in request.files:
#             update_profile_pic(output)
#             return redirect(url_for("users.edit", id=id))
#         if "image_file" in request.files:
#             create_gallery_image(output)
#             return redirect(url_for("users.show", username=current_user.username))
#     else:
#         return redirect("/<id>")