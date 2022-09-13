import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from forms import AddImageForm

# from forms import EditUserForm, UserAddForm, LoginForm, MessageForm, CSRFProtectForm
# from models import LikedMessage, db, connect_db, User, Message

load_dotenv()

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)


# home/index page shows collection of all photos with search and add button
    # if search term, re-render home page route with query string

# add image form page
# individual image page with edit button for options
    # if edit, make copy of photo to backend, commit to db, redirect to home




@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = AddImageForm()

    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'photos', filename
        ))
        return redirect(url_for('index'))

    return render_template('upload.html', form=form)