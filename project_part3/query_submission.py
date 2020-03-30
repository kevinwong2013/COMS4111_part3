from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class query_submission (FlaskForm):
    query = StringField('query')
    submit = SubmitField('submit query')