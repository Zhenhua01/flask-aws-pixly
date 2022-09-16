"""SQLAlchemy models for Pixly."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

import sqlalchemy as sa
from sqlalchemy import desc, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
class TSVector(sa.types.TypeDecorator):
    impl = TSVECTOR


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

    filename = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
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

    __ts_vector__ = db.Column(TSVector(),db.Computed(
         "to_tsvector('english', image_name || ' ' || notes || ' ' || uploaded_by)",
         persisted=True))
    __table_args__ = (Index('ix_image___ts_vector__',
          __ts_vector__, postgresql_using='gin'),)


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

    __ts_vector__ = db.Column(TSVector(),db.Computed(
         "to_tsvector('english', name || ' ' || value)",
         persisted=True))
    __table_args__ = (Index('ix_metadata___ts_vector__',
          __ts_vector__, postgresql_using='gin'),)

    # exif_data = db.Column(
    #     db.JSON,
    #     nullable=True
    # )

def connect_db(app):
    """Connect this database to Flask app."""

    db.app = app
    db.init_app(app)
