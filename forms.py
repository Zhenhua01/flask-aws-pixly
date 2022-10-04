"""WTForms for Pixly."""

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectMultipleField,
    SelectField, IntegerField, PasswordField)


class AddImageForm(FlaskForm):
    """ Form for adding images. """

    photo = FileField('JPG Image to upload:', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'JPG images only!')])

    image_name = StringField('Image Name:', validators=[
        DataRequired(),
        Length(max=50)])

    uploaded_by = StringField('Uploaded by:', validators=[
        DataRequired(),
        Length(max=50)])

    notes = TextAreaField('Notes:')


class EditImageForm(FlaskForm):
    """ Form for editing image. """

    tone = SelectField(
        'Tone',
        choices=[
            ('original', "Original"),
            ('sepia', "Sepia"),
            ("black_white", "Black & White")],
        default="original")

    border = SelectField(
        'Border Color (30px wide)',
        choices=[
            ("no_border", "No Border"),
            ("black", "Black"),
            ("white", "White"),
            ("grey", "Grey"),
            ("red", "Red"),
            ("green", "Green"),
            ("blue", "Blue"),
            ("yellow", "Yellow"),
            ],
        default="no_border")

    edge_detection = SelectMultipleField(
        'Edge Detection (hold shift to select multiple)',
        choices=[
            ("smooth", "Smooth"),
            ("enhance", "Enhance"),
            ("edges", 'Edge Outline'),
        ])

    reduce = IntegerField(
        'Scale Resolution Down (1x-10x)',
        validators=[NumberRange(min=1, max=10), Optional()])

    red = IntegerField('Add an overall red tint (%)', validators=[
        NumberRange(min=0, max=100), Optional()])

    green = IntegerField('Add an overall green tint (%)', validators=[
        NumberRange(min=0, max=100), Optional()])

    blue = IntegerField('Add an overall blue tint (%)', validators=[
        NumberRange(min=0, max=100), Optional()])


class EditImageUploadForm(FlaskForm):
    """ Form for adding an edited image. """

    filename = StringField('File Name:', validators=[
        DataRequired(),
        Length(max=50)])

    image_name = StringField('Image Name:', validators=[
        DataRequired(),
        Length(max=50)])

    uploaded_by = StringField('Uploaded by:', validators=[
        DataRequired()])

    notes = TextAreaField('Notes:')


class DeleteImageForm(FlaskForm):
    """ Form for admin code to delete an image. """

    code = PasswordField('Please confirm delete with admin code:', validators=[
        DataRequired(),
        Length(max=30)])
