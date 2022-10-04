"""Image View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_image_views.py


import os
from unittest import TestCase
from models import db, Image, Image_Metadata

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///pixly_test"

# Now we can import app
from app import app

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()

# Turn off CSRF for testing only
app.config['WTF_CSRF_ENABLED'] = False


class BaseViewTestCase(TestCase):
    def setUp(self):
        Image_Metadata.query.delete()
        Image.query.delete()

        image = Image(
            image_name="test",
            uploaded_by="test_user",
            notes="notes",
            filename="testfile.jpg",
            s3_url_path="https://pixlybucket.s3.us-west-1.amazonaws.com/sampleone.JPG"
        )

        db.session.add(image)
        db.session.commit()

        self.image_id = image.id

        image_metadata = Image_Metadata(
            image_id=image.id,
            tag="resolution",
            value="high quality",
        )

        db.session.add(image_metadata)
        db.session.commit()

        self.image_metadata_id = image_metadata.id

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()


    def test_home_page(self):
        """Tests if home page renders correctly."""

        with self.client as c:

            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="search-form"', html)
            self.assertIn('Add New Image', html)
            self.assertIn('class="image_card', html)


    def test_add_image(self):
        """Tests add image page renders correctly."""

        with self.client as c:

            resp = c.get('/addimage')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="add-image-form"', html)
            self.assertIn('type="submit"', html)


    def test_image_detail(self):
        """Tests image detail page renders correctly """

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('class="image', html)
            self.assertIn('class="image-detail', html)
            self.assertIn('Notes', html)

    def test_edit_image(self):
        """Tests edit image page renders correctly."""

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="edit-image-form"', html)
            self.assertIn('class="image', html)
            self.assertIn('type="submit"', html)

    def test_edit_image_preview(self):
        """Tests edited image preview page renders correctly."""

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}/edit/preview')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('class="image', html)
            self.assertIn('"/image/uploadedit"', html)
            self.assertIn('class="btn btn', html)

    def test_upload_edit(self):
        """Tests edited image upload page renders correctly."""

        with self.client as c:

            resp = c.get('/image/uploadedit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('class="image', html)
            self.assertIn('id="upload-edit-form"', html)
            self.assertIn('type="submit"', html)

    def test_delete_image(self):
        """Tests deleting image page renders correctly."""

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}/delete')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('class="image', html)
            self.assertIn('id="delete-image-form"', html)
            self.assertIn('type="submit"', html)


    def test_invalid_routes(self):
        """Tests invalid route redirects to home page."""

        with self.client as c:

            resp = c.get('/wrongroute', follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add New Image', html)
            self.assertIn('Invalid URL route', html)
