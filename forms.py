from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField, DecimalField, RadioField,FloatField, SubmitField,PasswordField
from wtforms.validators import InputRequired, Length, NumberRange, URL, Optional


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class PickForm(FlaskForm):
    """Form for adding picks."""
    # category = RadioField("Category", validators = [InputRequired()], choices=[ ('risk', 'Risk'),  ('to_win', 'To Win')])

    risk_amount = FloatField(
        "Risk Amount",
        validators=[InputRequired(), NumberRange(min=1, max=10)],
    )


class ConfirmForm(FlaskForm):
    """Confirm Form to submit pick"""

    submit = SubmitField()