"""WTForms for Pixly."""

from argparse import OPTIONAL
from signal import valid_signals
from typing import Optional
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, RadioField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
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
            (1, "Default"),
            (2, "Sepia"),
            (3, "Black & White")],
        coerce=int,
        default=1)

    border = SelectField(
        'Border',
        choices=[
            ("no border", "Default"),
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
        'Scale Down by',
        validators=[NumberRange(min=1, max=7), Optional()])

    red = IntegerField('RGB red hue (%)', validators=[
        NumberRange(min=0, max=100), Optional()])

    green = IntegerField('RGB green hue (%)', validators=[
        NumberRange(min=0, max=100), Optional()])

    blue = IntegerField('RGB blue hue (%)', validators=[
        NumberRange(min=0, max=100), Optional()])


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
