"""WTForms for Pixly."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed


class AddImageForm(FlaskForm):
    """ Form for adding images. """

    photo = FileField('Image to upload:', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'JPG images only!')])

    image_name = StringField('Image Name:', validators=[
        DataRequired(),
        Length(max=50)])

    uploaded_by = StringField('Uploaded by:', validators=[DataRequired()])

    notes = TextAreaField('Notes:')


class EditImageForm(FlaskForm):
    """ Form for editing image. """

    tone = SelectField(
        'Tone',
        choices=[
            (1, "Original"),
            (2, "Sepia"),
            (3, "Black & White")],
        coerce=int,
        default=1)

    border = SelectField(
        'Border (color)',
        choices=[
            ("no border", "No Border"),
            ("black", "Black"),
            ("white", "White"),
            ("grey", "Grey"),
            ("brown", "Brown")],
        default="no border")

    edge_detection = SelectMultipleField(
        'Edge Detection (Hold shift to select multiple)',
        choices=[
            ("Smooth", "Smooth"),
            ("Edges", 'Edges'),
            ("Enhance", "Enhance")
        ])

    reduce = IntegerField(
        'Scale Down by (1x-10x)',
        validators=[NumberRange(min=1, max=10), Optional()])

    red = IntegerField('Add RGB red tint (%)', validators=[
        NumberRange(min=0, max=100), Optional()])

    green = IntegerField('Add RGB green tint (%)', validators=[
        NumberRange(min=0, max=100), Optional()])

    blue = IntegerField('Add RGB blue tint (%)', validators=[
        NumberRange(min=0, max=100), Optional()])


class EditImageForUploadForm(FlaskForm):
    """ Form for adding images. """

    file_name = StringField('File Name:', validators=[
        DataRequired(),
        Length(max=50)])

    image_name = StringField('Image Name:', validators=[
        DataRequired(),
        Length(max=50)])

    uploaded_by = StringField('Uploaded by:', validators=[
        DataRequired()])

    notes = TextAreaField('Notes:')
