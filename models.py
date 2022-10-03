"""SQLAlchemy models for Pixly."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR

db = SQLAlchemy()

class TSVector(sa.types.TypeDecorator):
    impl = TSVECTOR

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
        db.String(50),
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

    s3_url_path = db.Column(
        db.String,
        nullable=False,
    )

    __ts_vector__ = db.Column(TSVector(),db.Computed(
         "to_tsvector('english', image_name || ' ' || uploaded_by || ' ' || notes)",
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

    tag = db.Column(
        db.String(100),
        nullable=False
    )

    value = db.Column(
        db.String(100),
        nullable=False
    )

    __ts_vector__ = db.Column(TSVector(),db.Computed(
         "to_tsvector('english', tag || ' ' || value)",
         persisted=True))

    __table_args__ = (Index('ix_metadata___ts_vector__',
          __ts_vector__, postgresql_using='gin'),)


def connect_db(app):
    """Connect this database to Flask app."""

    db.app = app
    db.init_app(app)
