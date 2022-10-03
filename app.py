import os
import boto3
import random
from dotenv import load_dotenv

from flask import Flask, render_template, flash, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from models import Image, Image_Metadata, db, connect_db
from forms import AddImageForm, EditImageForm, EditImageUploadForm, DeleteImageForm
from sqlalchemy.exc import IntegrityError
from botocore.exceptions import ClientError

from io import BytesIO
from image_processing import (
    search_images, extract_exif, image_editor, save_image)
from PIL import Image as PilImage


load_dotenv()

app = Flask(__name__)
connect_db(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

SECRET_DELETE_KEY = os.environ['SECRET_DELETE_KEY']

# boto3 client for image uploading to aws-s3 server
s3 = boto3.client(
        "s3",
        "us-west-1",
        aws_access_key_id = os.environ['ACCESS_KEY_ID'],
        aws_secret_access_key = os.environ['SECRET_ACCESS_KEY'])
BUCKET_NAME = os.environ['BUCKET_NAME']


@app.get('/')
def homepage():
    """Display home page with list of top 12 images or display search results."""

    search = request.args.get('search') and request.args.get('search').lower()
    if search:
        images = search_images(search)
    else:
        images = Image.query.limit(12).all()

    random.shuffle(images)

    return render_template('index.html', images=images, search=search)


@app.route('/addimage', methods=['GET', 'POST'])
def add_image():
    """ Get: Renders form to add a new image, add_image html.
        Post: Saves form data to database, uploads image to S3,
        and redirects to image details page. """

    form = AddImageForm()

    if form.validate_on_submit():
        filename = secure_filename(photo.filename)

        if Image.query.filter_by(filename = filename).first():
            flash("Filename already exists, please rename the file.", 'danger')
            return redirect('/addimage')

        # read photo data as binary and upload to s3 server
        try:
            photo = form.photo.data
            img = BytesIO(photo.read())
            s3.upload_fileobj(img, BUCKET_NAME, filename)
        except ClientError:
            flash("Image could not be uploaded to server.", 'danger')
            return redirect('/addimage')

        # save form data and aws-s3 url path to database
        image = Image(
            image_name=form.image_name.data,
            uploaded_by=form.uploaded_by.data,
            notes=form.notes.data,
            filename=filename,
            s3_url_path=f"http://{BUCKET_NAME}.s3.us-west-1.amazonaws.com/{filename}"
        )

        try:
            db.session.add(image)
            db.session.commit()
        except IntegrityError:
            flash("Form data could not be saved, please try again.", 'danger')
            return redirect('/addimage')

        # get exif_data from photo and save to database
        exif_data = extract_exif(photo)
        for tag in exif_data:
            metadata = Image_Metadata(
                image_id=image.id,
                tag=tag,
                value=exif_data[tag]
            )
            db.session.add(metadata)

        try:
            db.session.commit()
        except IntegrityError:
            flash("Image EXIF data could not be saved.", 'warning')

        flash("Image successfully uploaded!", 'success')
        return redirect(f"/image/{image.id}")

    return render_template('add_image.html', form=form)


@app.get('/image/<int:id>')
def show_image(id):
    """ Get: Renders image detail page, image.html"""

    try:
        image = Image.query.get_or_404(id)
        return render_template('image.html', image=image)
    except:
        flash("Image ID not found.", 'danger')
        return redirect('/')


@app.route('/image/<int:id>/edit', methods=['GET', 'POST'])
def edit_image(id):
    """ Get: Renders form to select image edits, edit_image.html.
        Post: Process image edits and displays preview page."""

    try:
        image = Image.query.get_or_404(id)
    except:
        flash("Image ID not found.", 'danger')
        return redirect('/')

    img = save_image(image.s3_url_path)
    form = EditImageForm()

    if form.validate_on_submit():

        img = image_editor(img, form)

        return redirect(f"/image/{id}/edit/preview")

    return render_template('edit_image.html', image=image, form=form, size=img.size)


@app.get('/image/<int:id>/edit/preview')
def preview_edit(id):
    """ Get: Renders preview page of edited image, preivew_edit.html. """

    try:
        Image.query.get_or_404(id)
    except:
        flash("Image ID not found.", 'danger')
        return redirect('/')

    img = PilImage.open("static/temp/image_edit.jpg")

    flash("Image edits applied", 'info')
    return render_template('preview_edit.html', id=id, size=img.size)


@app.route('/image/uploadedit', methods=['GET', 'POST'])
def upload_edit_image():
    """ Get: Renders form to upload an edited image.
        Post: Saves form data to database, uploads image to S3,
        and redirects to image details page. """

    form = EditImageUploadForm()

    if form.validate_on_submit():
        filename = form.filename.data

        if Image.query.filter_by(filename = filename).first():
            flash("Filename already exists, please rename the image.", 'danger')
            return redirect('/addimage')

        with open("static/temp/image_edit.jpg", 'rb') as img:
            try:
                s3.upload_fileobj(img, BUCKET_NAME, filename)
            except ClientError:
                flash("Image could not be uploaded to server", 'danger')
                return redirect('/image/uploadedit')

        # save form data and aws-s3 url path to database
        image = Image(
            image_name=form.image_name.data,
            uploaded_by=form.uploaded_by.data,
            filename=filename,
            notes=form.notes.data,
            s3_url_path=f"http://{BUCKET_NAME}.s3.us-west-1.amazonaws.com/{filename}"
        )

        try:
            db.session.add(image)
            db.session.commit()
            img = PilImage.open("static/temp/default_img.jpg")
            img.save("static/temp/image_edit.jpg")
        except IntegrityError:
            flash("Form data could not be saved, please try again.", 'danger')
            return redirect('/image/uploadedit')

        flash("Image successfully uploaded!", 'success')
        return redirect(f'/image/{image.id}')

    return render_template('upload_edit.html', form=form)


@app.route('/image/<int:id>/delete', methods=['GET', 'POST'])
def delete_image(id):

    try:
        image = Image.query.get_or_404(id)
    except:
        flash("Image ID not found.", 'danger')
        return redirect('/')

    form = DeleteImageForm()

    if form.validate_on_submit():
        code = form.code.data

        if code == SECRET_DELETE_KEY:
            try:
                s3.delete_object(
                    Bucket=BUCKET_NAME,
                    Key=image.filename)
            except ClientError:
                print(ClientError)
                flash("Image could not be deleted to server", 'warning')
                return redirect(f'/image/{image.id}/delete')

            Image_Metadata.query.filter(Image_Metadata.image_id == image.id).delete()
            db.session.delete(image)
            db.session.commit()

            flash("Image deleted from server", 'info')
            return redirect('/')
        else:
            flash("Invalid delete code.", 'warning')
            return redirect(f'/image/{image.id}/delete')

    return render_template('delete_image.html', image=image, form=form)



@app.route('/<string:path>')
def catch_all(path):
    """Function to catch all invalid routes and redirect to home page. """

    flash("Invalid URL route.", 'warning')
    return redirect('/')

