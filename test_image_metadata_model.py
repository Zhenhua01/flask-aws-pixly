"""Image_Metadata model tests."""

# run these tests like:
#
#    python -m unittest test_image_metadata_model.py


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


class ImageMetadataModelTestCase(TestCase):
    def setUp(self):
        Image_Metadata.query.delete()
        Image.query.delete()

        image = Image(
            image_name="test",
            uploaded_by="test_user",
            notes="notes",
            filename="testfile.jpg",
            amazon_file_path="http://test.s3.us-west-1.amazonaws.com/testfile.jpg"
        )

        db.session.add(image)
        db.session.commit()

        self.image_id = image.id

        image_metadata = Image_Metadata(
            image_id=image.id,
            name="resolution",
            value="high quality",
        )

        db.session.add(image_metadata)
        db.session.commit()

        self.image_metadata_id = image_metadata.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_image_model(self):
        """test if image is created successfully"""

        metadata1 = Image_Metadata.query.get(self.image_metadata_id)

        self.assertEqual(metadata1.image_id, self.image_id)
        self.assertEqual(metadata1.name, 'resolution')
        self.assertEqual(metadata1.value, "high quality")

    def test_empty_text(self):
        """ test image model error for empty image string"""

        new_metadata = Image_Metadata(
            image_id=self.image_id,
            name="resolution",
            value=None,
        )

        db.session.add(new_metadata)

        self.assertRaises(IntegrityError, db.session.commit)
