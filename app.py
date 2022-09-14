import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from models import db, connect_db, Image
from forms import AddImageForm
from botocore.exceptions import ClientError

import boto3
from PIL import Image as pillow

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


# TODO: editing image, do we replace and reupload?
# do we send back a presigned url for user to download? send back a link to serve image

@app.get('/')
def homepage():
    """Display home page with list of top 20 images."""
    # query db for amazon links (img url)
    images = Image.query.all()
    # try:
    # response = s3.generate_presigned_url(
    #     'get_object',
    #     Params={'Bucket': "pixly-bucket",
    #             'Key': "samplecat.jpg"},
    #     ExpiresIn=3600)
    # print(response)
    # except ClientError as e:
    #     # logging.error(e)
    #     print(e)
    #     return None

    # The response contains the presigned URL

    return render_template('index.html', images=images)


@app.route('/addimage', methods=['GET', 'POST'])
def upload():
    form = AddImageForm()

    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(filename))
        s3.upload_file(filename, BUCKET, filename)

        # insert image data to images table
        image_name = form.image_name.data
        uploaded_by = form.uploaded_by.data
        notes = form.notes.data

        image = Image(
            image_name=image_name,
            file_name=filename,
            uploaded_by=uploaded_by,
            notes=notes,
            amazon_file_path=f"http://{BUCKET}.s3.us-west-1.amazonaws.com/{filename}"
        )

        # insert image metadata to Image_Metadata table
        image = Image.open(f)

        db.session.add(image)
        db.session.commit()

        return redirect("/")

    return render_template('add_image.html', form=form)
