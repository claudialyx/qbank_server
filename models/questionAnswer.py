from models.base_model import BaseModel
import peewee as pw
from models.question import *
from playhouse.postgres_ext import TSVectorField


class QuestionAnswer(BaseModel):
    # question_id = pw.ForeignKeyField(Question, backref="QuestionAnswers")
    # choices_index = pw.IntegerField(index=True)
    # choices_text = pw.TextField(index=True)
    # search_content= TSVectorField(index=True, null=True)
    # question_id = pw.CharField(index=True)
    question_id = pw.IntegerField(index=True)
    choices_index = pw.IntegerField(index=True)
    choices_text = pw.TextField(index=True)
    search_content= TSVectorField(index=True)

# issues encountered:
# ValueError: invalid literal for int() with base 10: 'QID208'
# Reason: ForeignKeyField can only hold an integer, but question_id has "QID" so it throws an error
# Solution: Remove the usage of ForeignKeyField
