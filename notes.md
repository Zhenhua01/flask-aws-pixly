# Pix.ly: Image lighttable / editor»
- (Login/authentication isn’t required; any web user can do everything)
- Users can view photos stored in the system
- Users can add a JPG photo using an upload form and picking a file on their   computer (you’ll need to learn how to allow image uploads!)
- System will retrieve metadata from the photo (location of photo, model of camera, etc) and store it into the database (you’ll need to learn how to read the metadata from photos!)
- Images themselves are stored to Amazon S3, not in the database (you’ll get to practice using AWS!)
- Users can search image data from the EXIF fields (you can learn about PostgreSQL full-text search)
- Users can perform simple image edits (for example): - turning color photos into B&W - adding sepia tones - reducing the size of the image - adding a border around the image

# Frontend:
    - Jinja render templates
		- list images, search images, editing images
	- allow image uploads from computer in forms
		- upload info form

# Backend:
	- Python Flask Server
	- Pillow library for processing
		- can this edit images (colors/borders/etc)
		- editing photo makes a new copy and uploads as new
		- get meta data from user upload
	- SQLA (psycopg2) for db of images
		- store image data, metadata
		- store AWS S3 address of photo
	- WTForms for form validation, require name of image and an image
	- EXIF fields for image data search
		- PSQL full-text search on exif table
	- dotenv library for secret keys/access keys (create .env file with env vars)

# Database:
    - One table for Image Table:
        - ID: PK
        - Image name (from form)
        - notes (from form)
        - file name.jpg
        - upload date
        - path to aws s3

    - One table for EXIF fields: (what is in EXIF fields?)
        - .getExif method from pillow
        - PK: FK to table images.id
        - store json data in sql:
            - create date
            - location
            - author
            - camera model (includes mnfr)
            - exposure
            - other exif data???