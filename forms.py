"""WTForms for Pixly."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed

class AddImageForm(FlaskForm):
    """Form for adding users."""

    photo = FileField('Image to upload:', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'JPG images only!')])

    image_name = StringField('Image Name:', validators=[
        DataRequired(),
        Length(max=50)])

    uploaded_by = StringField('Uploaded by:', validators=[DataRequired()])

    notes = TextAreaField('Notes:')

