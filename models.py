
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_moment import Moment
# from flask import (Flask, 
#                   render_template)

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)



# Models.
#----------------------------------------------------------------------------#
#wendy: add association tables 
show_venue_assc = db.Table('show_venue_assc',
  db.Column('venue_id',db.Integer, db.ForeignKey('venue.id'),primary_key = True),
  db.Column('show_id',db.Integer, db.ForeignKey('show.id'), primary_key = True)
)
show_artist_assc = db.Table('show_artist_assc',
  db.Column('artist_id',db.Integer, db.ForeignKey('artist.id'),primary_key = True),
  db.Column('show_id',db.Integer, db.ForeignKey('show.id'), primary_key = True)
)
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
     # cTODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean())
    seeking_description =  db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    show = db.relationship('Show',secondary = show_venue_assc, backref = db.backref('venue',lazy = 'dynamic'),lazy = 'dynamic')
    # past_shows_count = db.Column(db.Integer)
    # upcoming_shows_count = db.Column(db.Integer)
  
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
#    genres = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    # cTODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    show = db.relationship('Show',secondary = show_artist_assc, backref = db.backref('artist',lazy = 'dynamic'),lazy = 'dynamic')

class Show(db.Model):
    __tablename__= 'show'

    id = db.Column(db.Integer, primary_key = True)
    start_time = db.Column(db.DateTime)