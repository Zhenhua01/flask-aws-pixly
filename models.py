"""SQLAlchemy models for Pixly."""

from datetime import datetime
from unicodedata import name
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Image(db.Model):
    """Table for images."""

    __tablename__ = 'images'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    image_name = db.Column(
        db.String(50),
        nullable=False
    )

    uploaded_by = db.Column(
        db.String,
        nullable=False
    )

    notes = db.Column(
        db.String
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    amazon_file_path = db.Column(
        db.String,
        nullable=False
    )


class Image_Metadata(db.Model):
    """Table for images metadata."""

    __tablename__ = 'metadata'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    image_id = db.Column(
        db.Integer,
        db.ForeignKey('images.id'),
        nullable=False
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

    value = db.Column(
        db.String(50),
        nullable=False
    )

    # exif_data = db.Column(
    #     db.JSON,
    #     nullable=True
    # )

def connect_db(app):
    """Connect this database to Flask app."""

    db.app = app
    db.init_app(app)
