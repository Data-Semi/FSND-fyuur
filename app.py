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
from models import *

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
  # cTODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data =[]

  for venue in venues:
    shows = venue.show
    numUpcomingShows = (shows.filter(Show.start_time > dt.now())).count()
    venue_data = {
      "id" : venue.id,
      'name' : venue.name,
      'num_upcoming_shows' : numUpcomingShows
    }
    data.append(venue_data)
    
  response={
    "count": len(data),
    "data": data
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
  # cTODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

#wendy: debug process  
# vagrant@vagrant:/vagrant/projects/1_fyyur/FSND-fyuur$ python3
# >>> from app import db,Venue,Show,Artist
# >>> Venue.query.all()
# [<Venue 1>, <Venue 2>, <Venue 3>, <Venue 4>]
# >>> from app import delete_venue
# >>> delete_venue(4)
# >>> Venue.query.all()
# [<Venue 1>, <Venue 2>, <Venue 3>]
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
  # cTODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  data =[]

  for artist in artists:
    shows = artist.show
    numUpcomingShows = (shows.filter(Show.start_time > dt.now())).count()
    artist_data = {
      "id" : artist.id,
      'name' : artist.name,
      'num_upcoming_shows' : numUpcomingShows
    }
    data.append(artist_data)
    
  response={
    "count": len(data),
    "data": data
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
  artist=Artist.query.get(artist_id)
  # cTODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # cTODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  #for debug
  error=False
  artist=Artist.query.get(artist_id)
  if not form.validate():
    flash('Input error! Please check again.')
    return render_template('forms/edit_artist.html', form=form,artist=artist)
  try:
    artist = Artist.query.get(artist_id)
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    artist.facebook_link=request.form['facebook_link']
    artist.genres=request.form.getlist('genres')
#      seeking_talent=request.form['seeking_talent']
#      seeking_description=request.form['seeking_description']
    if len(artist.genres) > 10:
      flash('No more than 10 genres please')
      return render_template('forms/edit_artist.html', form=form,artist=artist)
    #  return redirect(url_for('create_venue_form')) #this way will clear all of previous input in the page.
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully edited!')
  except:
    error = True
    flash('An error occurred. Artist ' + artist.name + ' could not be edited.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # cTODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
#  return render_template('pages/home.html')
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # cTODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # cTODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  #for debug
  error=False
  venue=Venue.query.get(venue_id)
  if not form.validate():
    flash('Input error! Please check again.')
    return render_template('forms/edit_venue.html',form=form,venue=venue)
  try:
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state=request.form['state']
    venue.phone=request.form['phone']
    venue.facebook_link=request.form['facebook_link']
    venue.genres=request.form.getlist('genres')
#      seeking_talent=request.form['seeking_talent']
#      seeking_description=request.form['seeking_description']
    if len(venue.genres) > 10:
      flash('No more than 10 genres please')
      return render_template('forms/edit_artist.html', form=form,artist=artist)
    #  return redirect(url_for('create_venue_form')) #this way will clear all of previous input in the page.
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully edited!')
  except:
    error = True
    flash('An error occurred. Venue ' + venue.name + ' could not be edited.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # cTODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
#  return render_template('pages/home.html')
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
  # cTODO: insert form data as a new Venue record in the db, instead
  # cTODO: modify data to be the data object returned from db insertion
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
  data= Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # cTODO: insert form data as a new Show record in the db, instead
  #wendy: to solve: <class 'sqlalchemy.exc.IntegrityError'>, IntegrityError
  #  postgresql=# select setval ('show_id_seq', (SELECT MAX(id) FROM show));
  form = ShowForm(request.form)
  #for debug
  error=False
  if not form.validate():
    flash('Input error! Please check again.')
    return render_template('forms/new_show.html', form=form)
  try:
    start_time=request.form['start_time']
    #  return redirect(url_for('create_venue_form')) #this way will clear all of previous input in the page.
    show = Show(start_time=start_time)
    print(request.form['venue_id'])
    print(Venue.query.get(request.form['venue_id']))
    show.venue=[Venue.query.get(request.form['venue_id'])]
    show.artist=[Artist.query.get(request.form['artist_id'])]
    db.session.add(show)
    db.session.commit()
    db.session.close()
    flash('Show at' + start_time + ' was successfully listed!')
  except:
    error = True
    flash('An error occurred. Show at ' + start_time + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # cTODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
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

