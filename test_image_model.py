"""Image model tests."""

# run these tests like:
#
#    python -m unittest test_image_model.py

from sqlalchemy.exc import IntegrityError
from models import db, Image, Image_Metadata
from unittest import TestCase
import os

# from psycopg2 import errors

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///pixly_test"

# Now we can import app
from app import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()


class ImageModelTestCase(TestCase):
    def setUp(self):
        Image_Metadata.query.delete()
        Image.query.delete()

        image = Image(
            image_name="test_name",
            uploaded_by="test_user",
            notes="test_notes",
            filename="testfile.jpg",
            s3_url_path=f"http://test.s3.us-west-1.amazonaws.com/testfile.jpg"
        )

        db.session.add(image)
        db.session.commit()

        self.image_id = image.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_image_model(self):
        """Test if image metadata is created successfully."""

        img1 = Image.query.get(self.image_id)

        self.assertEqual(img1.filename, 'testfile.jpg')
        self.assertEqual(img1.notes, 'test_notes')

    def test_empty_text(self):
        """Test if image metadata model error for empty image name."""

        new_img = Image(
            image_name=None,
            uploaded_by="test_user",
            notes="notes",
            filename="testfile.jpg",
            s3_url_path=f"http://test.s3.us-west-1.amazonaws.com/testfile.jpg"
        )
        db.session.add(new_img)
        self.assertRaises(IntegrityError, db.session.commit)
