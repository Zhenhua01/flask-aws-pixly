import os
from dotenv import load_dotenv

from flask import Flask, render_template, flash, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from models import Image, Image_Metadata, db, connect_db
from forms import AddImageForm, EditImageForm, EditImageForUploadForm
from botocore.exceptions import ClientError

import requests
import boto3
from io import BytesIO
from PIL import Image as PilImage, ImageFilter, TiffImagePlugin, ImageOps
from PIL.ExifTags import TAGS
from helpers import sepia, custom_colors


load_dotenv()

app = Flask(__name__)
connect_db(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

# ACCESS_KEY_ID = os.environ['ACCESS_KEY_ID']
# SECRET_ACCESS_KEY = os.environ['SECRET_ACCESS_KEY']
# BUCKET = os.environ['BUCKET_NAME']

s3 = boto3.client(
    "s3",
    "us-west-1",
    aws_access_key_id=os.environ['ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['SECRET_ACCESS_KEY']
)
BUCKET = os.environ['BUCKET_NAME']

# home/index page shows collection of all photos with search and add button
# if search term, re-render home page route with query string

# add image form page
# individual image page with edit button for options
# if edit, make copy of photo to backend, commit to db, redirect to home

# //TODO: boto3 client functions/helpers, import .env var


@app.get('/')
def homepage():
    """Display home page with list of top 10 images or display search results."""

    search = request.args.get('search') and request.args.get('search').lower()
    if not search:
        images = Image.query.limit(10).all()
    else:
        id_list = []

        metadata_search = Image_Metadata.query.filter(
            Image_Metadata.__ts_vector__.match(search)).all()

        for metadata in metadata_search:
            id_list.append(metadata.image_id)

        image_search = Image.query.filter(
            Image.__ts_vector__.match(search)).all()

        for image in image_search:
            id_list.append(image.id)

        unique_ids = set(id_list)

        images = Image.query.filter(Image.id.in_(unique_ids)).all()

    return render_template('index.html', images=images, search=search)


@app.route('/addimage', methods=['GET', 'POST'])
def add_image():
    """ Get: Renders add_image html """
    form = AddImageForm()

    if form.validate_on_submit():
        f = form.photo.data

        filename = secure_filename(f.filename)
        f.save(os.path.join(filename))
        with open(filename, 'rb') as photo:
            # print(type(photo))
            s3.upload_fileobj(photo, BUCKET, filename)

        # delete image form app or use uploadfileobj

        # insert image data to images table
        image_name = form.image_name.data
        uploaded_by = form.uploaded_by.data
        notes = form.notes.data

        image = Image(
            image_name=image_name,
            uploaded_by=uploaded_by,
            notes=notes,
            filename=filename,
            amazon_file_path=f"http://{BUCKET}.s3.us-west-1.amazonaws.com/{filename}"
        )
        db.session.add(image)
        db.session.commit()

        os.remove(filename)

        # insert image metadata to Image_Metadata table
        img = PilImage.open(f)
        img_metadata = img.getexif()
        exif_data = {}

        for tag, data in img_metadata.items():
            if tag in TAGS:
                if isinstance(data, TiffImagePlugin.IFDRational):
                    data = float(data)
                elif isinstance(data, bytes):
                    data = data.decode(errors="replace")

                exif_data[TAGS[tag]] = data

        for tag in exif_data:
            metadata = Image_Metadata(
                image_id=image.id,
                name=tag,
                value=exif_data[tag]
            )
            db.session.add(metadata)
        db.session.commit()

        return redirect("/")

    return render_template('add_image.html', form=form)


@app.route('/image/<int:id>', methods=['GET'])
def show_image(id):
    image = Image.query.get_or_404(id)

    return render_template('image.html', image=image)


@app.route('/image/<int:id>/edit', methods=['GET', 'POST'])
def edit_image(id):
    image = Image.query.get_or_404(id)

    form = EditImageForm()

    filename = image.amazon_file_path
    print('refreshing here')
    response = requests.get(filename)
    img = PilImage.open(BytesIO(response.content))
    img.save("static/images/edit.JPG")

    size = img.size

    if form.validate_on_submit():
        rgb = [form.red.data or 100,
               form.green.data or 100,
               form.blue.data or 100]
        print('rgb is', rgb)

        img = custom_colors(img, rgb)
        if form.tone.data == 2:
            img = sepia(img)
        if form.tone.data == 3:
            img = ImageOps.grayscale(img)
        if form.border.data != "no border":
            img = ImageOps.expand(img, border=35, fill=form.border.data)
        if "Smooth" in form.edge_detection.data:
            img = img.filter(ImageFilter.SMOOTH)
        if "Edges" in form.edge_detection.data:
            img = img.filter(ImageFilter.FIND_EDGES)
        if "Enhance" in form.edge_detection.data:
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        if form.reduce.data:
            img = img.reduce(form.reduce.data)

        img.save("static/images/edit.JPG")
        return redirect(f"/image/{id}/edit/preview")

    return render_template('edit_image.html', image=image, size=size, form=form)


@app.get('/image/<int:id>/edit/preview')
def preview_edit(id):

    img = PilImage.open("static/images/edit.JPG")

    size = img.size

    return render_template('preview_edit.html', id=id, size=size)


@app.route('/uploadedit', methods=['GET', 'POST'])
def upload_edit_image():

    form = EditImageForUploadForm()

    if form.validate_on_submit():
        filename = form.file_name.data
        with open(os.path.join("static/images/edit.JPG"), 'rb') as photo:

            s3.upload_fileobj(photo, BUCKET, filename)

        image_name = form.image_name.data
        uploaded_by = form.uploaded_by.data
        notes = form.notes.data

        image = Image(
            image_name=image_name,
            uploaded_by=uploaded_by,
            notes=notes,
            filename=filename,
            amazon_file_path=f"http://{BUCKET}.s3.us-west-1.amazonaws.com/{filename}"
        )

        db.session.add(image)
        db.session.commit()

        os.remove("static/images/edit.jpg")

        return redirect(f'/image/{image.id}')

    return render_template('upload_edit.html', form=form)


# upload_fileobj so we do not need to write/delete to from app
# unique filename and error handlers
# write some tests?
