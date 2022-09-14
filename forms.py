"""WTForms for Pixly."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed

class AddImageForm(FlaskForm):
    """Form for adding users."""

    uploaded_by = StringField('Uploaded by', validators=[DataRequired()])

    image_name = StringField('Image Name', validators=[
        DataRequired(),
        Length(max=50)])

    notes = TextAreaField('Notes')

    photo = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'Images only!')])

