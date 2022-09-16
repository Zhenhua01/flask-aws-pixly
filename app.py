import os
from dotenv import load_dotenv

from flask import Flask, render_template, flash, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from models import Image, Image_Metadata, db, connect_db
from forms import AddImageForm, EditImageForm, EditImageForUploadForm
from sqlalchemy.exc import IntegrityError
from botocore.exceptions import ClientError

import requests
import random
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
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
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


@app.get('/')
def homepage():
    """Display home page with list of top 10 images or display search results."""

    search = request.args.get('search') and request.args.get('search').lower()
    if not search:
        images = Image.query.limit(10).all()
        random.shuffle(images)
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
    """ Get: Renders form to add a new image, add_image html.
        Post: Saves form data to database, uploads image to S3,
        and redirects to image details page. """

    form = AddImageForm()

    if form.validate_on_submit():
        f = form.photo.data

        filename = secure_filename(f.filename)
        f.save(os.path.join(filename))
        with open(filename, 'rb') as photo:
            try:
                s3.upload_fileobj(photo, BUCKET, filename)
            except ClientError:
                flash("Image upload was not successful", 'danger')
                return redirect('/addimage')

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
        try:
            db.session.add(image)
            db.session.commit()
            os.remove(filename)
        except IntegrityError:
            flash("Filename already exists, please rename the image.", 'danger')
            return redirect('/addimage')

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

        try:
            db.session.commit()
        except IntegrityError:
            flash("Image EXIF data could not be saved.", 'danger')

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

    form = EditImageForm()

    filename = image.amazon_file_path
    response = requests.get(filename)
    img = PilImage.open(BytesIO(response.content))
    img.save("static/images/edit.JPG")

    size = img.size

    if form.validate_on_submit():
        rgb = [form.red.data or 0,
               form.green.data or 0,
               form.blue.data or 0]
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
        flash("Image edits applied", 'info')
        return redirect(f"/image/{id}/edit/preview")

    return render_template('edit_image.html', image=image, size=size, form=form)


@app.get('/image/<int:id>/edit/preview')
def preview_edit(id):
    """ Get: Renders preview page of edited image, preivew_edit.html. """

    try:
        image = Image.query.get_or_404(id)
    except:
        flash("Image ID not found.", 'danger')
        return redirect('/')

    img = PilImage.open("static/images/edit.JPG")
    size = img.size

    return render_template('preview_edit.html', id=id, size=size)


@app.route('/uploadedit', methods=['GET', 'POST'])
def upload_edit_image():
    """ Get: Renders form to upload an edited image.
        Post: Saves form data to database, uploads image to S3,
        and redirects to image details page. """

    form = EditImageForUploadForm()

    if form.validate_on_submit():
        filename = form.file_name.data
        with open(os.path.join("static/images/edit.JPG"), 'rb') as photo:
            try:
                s3.upload_fileobj(photo, BUCKET, filename)
            except ClientError:
                flash("Image upload was not successful", 'danger')
                return redirect('/addimage')

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

        try:
            db.session.add(image)
            db.session.commit()
            os.remove("static/images/edit.jpg")
        except IntegrityError:
            flash("Filename already exists, please choose a different name.", 'danger')
            return redirect('/uploadedit')

        flash("Image successfully uploaded!", 'success')
        return redirect(f'/image/{image.id}')

    return render_template('upload_edit.html', form=form)


@app.route('/<string:path>')
def catch_all(path):
    """Function to catch all invalid routes and redirect to home page. """

    flash("Invalid URL route.", 'warning')
    return redirect('/')


# upload_fileobj so we do not need to write/delete to from app
# write some tests?

# experience:
#   - rediscovering flask & reading thru all 1000 pages of aws docs(static bucket), read thru pillow docs
#   - considering user interaction with site changed how we approached redirects and routing
#   - coming back to server-side rendering, react would've made app more dynamic(redirects)
#   - client side render > server side, seemed clunky
#   - opened eyes on how much we can deliver in a timeframe, too ambitious with react(not a single test)

# features:
#   - pillow, processes img and edits
#   - search(exif)

# bugs:
#   - format of exif data, psql can't store the metadata raw form which comes in as ifdrational
#   - (inefficient) writing/saving img to local before sending to amazon,then delete after upload
#       couldn't read img file properly with boto3/s3 upload_fileobj
#   - overlapping filenames in amazon are not distinguishable, will overwrite previous object in bucket
#       will need a unique column in db for filename because links for amazon objects dynamically generated by filename
#   - testing, on save, formatter moves app above environment declaration, wiped production db

# improvements for future(D I 2.0):
#   - react frontend (editing img will be more robust because re-renders after state change)
#   - full text search is not fully functional
#   - could potentially add users/auth | tags for photos and new db table relations
#   - more features like adding photos, albums
