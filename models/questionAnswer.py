from models.base_model import BaseModel
from models.question import Question
import peewee as pw


class QuestionAnswer(BaseModel):
    question_id = pw.CharField(index=True)
    choices_index = pw.IntegerField(index=True)
    choices_text = pw.TextField(index=True)

# issues encountered:
# ValueError: invalid literal for int() with base 10: 'QID208'
# Reason: ForeignKeyField can only hold an integer, but my question_id has "QID" so it throws an error
