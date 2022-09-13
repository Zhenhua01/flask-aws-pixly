from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed


class AddImageForm(FlaskForm):
    """Form for adding users."""

    author = StringField('Uploaded by', validators=[DataRequired()])
    image_name = StringField('Image Name', validators=[
        DataRequired(),
        Length(max=50)])
    image_file = FileField('Image', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'Images only!')])
    notes = TextAreaField('Notes')




