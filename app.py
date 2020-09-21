#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#wendy: Migration
from flask_migrate import Migrate
from datetime import datetime as dt
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
#wendy:migration
migrate = Migrate(app,db) 

# cTODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
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

# cTODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # cTODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data= Venue.query.all()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # cTODO: replace with real venue data from the venues table, using venue_id
    #   "past_shows": [{
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }],
    # "upcoming_shows": [],
  data= Venue.query.get(venue_id)
  shows = data.show
  
  upcoming_shows_query = shows.filter(Show.start_time > dt.now())
  past_shows_query = shows.filter(Show.start_time <= dt.now())
  #print(past_shows_query.all())
  upcoming_shows=[]
  past_shows=[]

  for show in upcoming_shows_query:
    show_data= {
      'artist_id':show.artist.first().id,
      'artist_name':show.artist.first().name,
      'artist_image_link':show.artist.first().image_link,
      "start_time": show.start_time,
    }
    #print(show.artist.first().id)
    upcoming_shows.append(show_data.copy())
  for show in past_shows_query:
    show_data= {
      'artist_id':show.artist.first().id,
      'artist_name':show.artist.first().name,
      'artist_image_link':show.artist.first().image_link,
      "start_time": show.start_time,
    }
    #print(show.artist.first().id)
    past_shows.append(show_data.copy())

  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  return render_template('pages/show_venue.html', venue=data,upcoming_shows=upcoming_shows,past_shows=past_shows,upcoming_shows_count=upcoming_shows_count,past_shows_count=past_shows_count)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # cTODO: insert form data as a new Venue record in the db, instead
 
  form = VenueForm(request.form)
  #for debug
  error=False
  if not form.validate():
    flash('Input error! Please check again.')
    return render_template('forms/new_venue.html', form=form)
  try:
    name=request.form['name']
    city=request.form['city']
    address=request.form['address']
    state=request.form['state']
    phone=request.form['phone']
    facebook_link=request.form['facebook_link']
    genres=request.form.getlist('genres')
#      seeking_talent=request.form['seeking_talent']
#      seeking_description=request.form['seeking_description']
    if len(genres) > 10:
      flash('No more than 10 genres please')
      return render_template('forms/new_venue.html', form=form)
    #  return redirect(url_for('create_venue_form')) #this way will clear all of previous input in the page.
    venue = Venue(name=name, city=city, address=address, state=state, 
    phone=phone, facebook_link=facebook_link, genres=genres)
    db.session.add(venue)
    db.session.commit()
    db.session.close()
    flash('Venue ' + name + ' was successfully listed!')
  except:
    error = True
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # cTODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #<--for debug...
  # if not error:
  #   flash('Venue ' + name + ' was successfully listed!')
  # else:
  #   print(ValidationError)
  #   flash('An error occurred. Venue ' + name + ' could not be listed.')
  #   return redirect(url_for('create_venue_form'))
  #..for debug -->
  return render_template('pages/home.html',form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # cTODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # cTODO: replace with real venue data from the venues table, using venue_id
  data= Artist.query.get(artist_id)
  shows = data.show
  
  upcoming_shows_query = shows.filter(Show.start_time > dt.now())
  past_shows_query = shows.filter(Show.start_time <= dt.now())
  #print(past_shows_query.all())
  upcoming_shows=[]
  past_shows=[]

  for show in upcoming_shows_query:
    show_data= {
      'venue_id':show.venue.first().id,
      'venue_name':show.venue.first().name,
      'venue_image_link':show.venue.first().image_link,
      "start_time": show.start_time,
    }
    #print(show.venue.first().id)
    upcoming_shows.append(show_data.copy())
  for show in past_shows_query:
    show_data= {
      'venue_id':show.venue.first().id,
      'venue_name':show.venue.first().name,
      'venue_image_link':show.venue.first().image_link,
      "start_time": show.start_time,
    }
    #print(show.venue.first().id)
    past_shows.append(show_data.copy())

  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
  return render_template('pages/show_artist.html', artist=data,upcoming_shows=upcoming_shows,past_shows=past_shows,upcoming_shows_count=upcoming_shows_count,past_shows_count=past_shows_count)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  #for debug
  error=False
  if not form.validate():
    flash('Input error! Please check again.')
    return render_template('forms/new_artist.html', form=form)
  try:
    name=request.form['name']
    city=request.form['city']
    state=request.form['state']
    phone=request.form['phone']
    facebook_link=request.form['facebook_link']
    genres=request.form.getlist('genres')
#      seeking_talent=request.form['seeking_talent']
#      seeking_description=request.form['seeking_description']
    if len(genres) > 10:
      flash('No more than 10 genres please')
      return render_template('forms/new_artist.html', form=form)
    #  return redirect(url_for('create_venue_form')) #this way will clear all of previous input in the page.
    artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link, genres=genres)
    db.session.add(artist)
    db.session.commit()
    db.session.close()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    error = True
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # cTODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # cTODO: replace with real venues data.
  data_p= PastShows.query.all()
  data_u= UpcomingShows.query.all()
  return render_template('pages/shows.html', shows=data_p+data_u)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ArtistForm(request.form)
  #for debug
  error=False
  if not form.validate():
    flash('Input error! Please check again.')
    return render_template('forms/new_artist.html', form=form)
  try:
    name=request.form['name']
    city=request.form['city']
    state=request.form['state']
    phone=request.form['phone']
    facebook_link=request.form['facebook_link']
    genres=request.form.getlist('genres')
#      seeking_talent=request.form['seeking_talent']
#      seeking_description=request.form['seeking_description']
    if len(genres) > 10:
      flash('No more than 10 genres please')
      return render_template('forms/new_artist.html', form=form)
    #  return redirect(url_for('create_venue_form')) #this way will clear all of previous input in the page.
    artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link, genres=genres)
    db.session.add(artist)
    db.session.commit()
    db.session.close()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    error = True
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # cTODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''
# Or specify port manually:

if __name__ == '__main__':
#    port = int(os.environ.get('PORT', 8000))
#    app.run(host='0.0.0.0', port=port)
#    app.debug=False
    app.run(host='0.0.0.0', port=5000,debug=True)

