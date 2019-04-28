from models.base_model import BaseModel
import peewee as pw
from playhouse.postgres_ext import TSVectorField


class Question(BaseModel):
    survey_id = pw.CharField(index=True)
    question_id = pw.CharField(unique=True)
    question_type = pw.CharField(index=True)
    question_text = pw.TextField(index=True)

    # to do a full text search on question_text:
    search_content = TSVectorField(index=True, null=True)
    # search_content = TSVectorField(question_text) # throws ref = error 001

    # ref = error 001
    # error when doing python migrate.py to implement full text search:
    # peewee.ProgrammingError: syntax error at or near "<"
    # LINE 1: ...STS "question_search_content" ON "question" USING <TextField...
    #                                                              ^

    # TRIED:
    # 1:flask shell
    # >>> from models.question import *
    # >>> from playhouse.postgres_ext import Match
    # >>> a = Question.select()&Match(Question.question_text, "drinks")
    # >>> a[0]
    # Traceback (most recent call last):
    #  File "C:\Users\User\Anaconda3\lib\site-packages\peewee.py", line 2714, in execute_sql
    #    cursor.execute(sql, params or ())
    # psycopg2.ProgrammingError: syntax error at or near "to_tsvector"
    # LINE 1: ...estion_text" FROM "question" AS "t1") INTERSECT ((to_tsvecto...
    #                                                             ^
    # b = Question.select().where(Question.question_id == "QID217")&Match(Question.question_text, "drinks")
    # >>> b[0]
    # same error

# **question_id = need to set to unique
# to implement: if id already exist, don't save in database again
