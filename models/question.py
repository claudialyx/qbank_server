from models.base_model import BaseModel
import peewee as pw
from playhouse.postgres_ext import TSVectorField


class Question(BaseModel):
    # survey_id = pw.CharField(index=True)
    # question_id = pw.IntegerField(unique=True)
    # question_type = pw.CharField(index=True)
    # question_text = pw.TextField(index=True)
    # # to do a full text search on question_text:
    # search_content = TSVectorField(index=True, null=True)
    survey_id = pw.CharField(index=True)
    question_id = pw.IntegerField(unique=True)
    # question_id = pw.CharField(unique=True)
    question_type = pw.CharField(index=True)
    question_text = pw.TextField(index=True)
    # to do a full text search on question_text:
    search_content = TSVectorField(index=True)
