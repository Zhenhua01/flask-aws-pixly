"""WTForms for Pixly."""

from argparse import OPTIONAL
from signal import valid_signals
from typing import Optional
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
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

    black_and_white = RadioField(
        'Black & White',
        choices=[(True, "yes"), (False, '')], coerce=bool)

    edge_detection = SelectMultipleField(
        'Edge Detection (Hold shift to select multiple)',
        choices=[
            ("Smooth", "Smooth"),
            ("Edges", 'Edges'),
            ("Enhance", "Enhance")
        ])

    reduce = SelectField(
        'Scale Down by',
        choices=[
            (1, "1x"),
            (2, "2x"),
            (3, "3x"),
            (4, "4x"),
            (5, "5x")], coerce=int)


class EditImageForUploadForm(FlaskForm):
    """ Form for adding images. """

    file_name = StringField('File Name:', validators=[
        DataRequired(),
        Length(max=50)])

    image_name = StringField('Image Name:', validators=[
        DataRequired(),
        Length(max=50)])

    uploaded_by = StringField('Uploaded by:', validators=[DataRequired()])

    notes = TextAreaField('Notes:')
