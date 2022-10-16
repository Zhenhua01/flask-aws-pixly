# Pixly Image App

[Live Demo (Heroku)](http://pixly-zhl.herokuapp.com)

Project: Full stack application for users to upload, edit, and save images. Users can also search stored images by keywords and image metadata automatically extracted from EXIF fields.

## Available Scripts

### Docker (optional):
To spin up containerized application, run this in the project directory.
Open [http://localhost:5001](http://localhost:5001) to view it in browser:

    docker-compose up -d

### In the project directory and venv, you can:

Create the app database and table schema:

    psql -f pixly.sql

App requires a `.env` file in the main directory with:
- SECRET_KEY = secret (or any secret key of choice)
- DATABASE_URL = postgresql:///pixly
- SECRET_DELETE_KEY = secret (or any secret key of choice)
- An AWS-S3 bucket you have access to:
    - BUCKET_NAME =
    - ACCESS_KEY_ID =
    - SECRET_ACCESS_KEY =

Install required dependencies from requirements.txt:

    pip3 install -r requirements.txt

Run the app in the development mode. Open [http://localhost:5001](http://localhost:5001) to view it in browser:

    flask run -p 5001

Run all tests:

    python3 -m unittest
