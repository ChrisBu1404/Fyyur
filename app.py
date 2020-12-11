#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import date
now= datetime.utcnow()

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))




class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    # Foreign Keys
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    # relationships
    artist = db.relationship(Artist,
        backref=db.backref('shows', cascade='all, delete')
    )
    venue = db.relationship(Venue,
        backref=db.backref('shows', cascade='all, delete')
    )


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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.all()

  data = []
  for venue in venues:
    data_temp={
      "city": venue.city,
      "state": venue.state,
      "venues": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 5,
      }]
    }

    data.append(data_temp)




  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 5,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  s_input = request.form.get('search_term')
  s_input ='%' + s_input + '%'
  venues = Venue.query.filter(Venue.name.like(s_input)).all()
  venue_count = Venue.query.filter(Venue.name.like(s_input)).count()

  data_list = []
  for venue in venues:
    data_list_temp= {
      "id" : venue.id,
      "name": venue.name
    }
    data_list.append(data_list_temp)

  response={
    "count": venue_count,
    "data": data_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcoming_shows_count = db.session.query(Venue).join(Show).filter_by(venue_id = venue_id).filter(Show.start_time>now).count()
  past_shows_count = db.session.query(Venue).join(Show).filter_by(venue_id = venue_id).filter(Show.start_time<now).count()
  past_shows = db.session.query(Show).join(Venue).filter_by(id = venue_id).filter(Show.start_time<now).all()
  past_shows_list = []
  for past_show in past_shows:
    time = past_show.start_time
    artist_id = past_show.artist_id
    artist_name = Artist.query.filter_by(id=artist_id).first().name
    past_shows_list_temp = {
      "start_time" : time.strftime('%c'),
      "artist_id" : artist_id,
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "artist_name" : artist_name
    }
    past_shows_list.append(past_shows_list_temp)

  upcoming_shows = db.session.query(Show).join(Venue).filter_by(id = venue_id).filter(Show.start_time>now).all()
  upcoming_shows_list = []
  for upcoming_show in upcoming_shows:
    time = upcoming_show.start_time
    artist_id = upcoming_show.artist_id
    artist_name = Artist.query.filter_by(id=artist_id).first().name
    upcoming_shows_list_temp = {
      "start_time" : time.strftime('%c'),
      "artist_id" : artist_id,
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "artist_name" : artist_name
    }
    upcoming_shows_list.append(upcoming_shows_list_temp)


  data = {
    "id": Venue.query.filter_by(id=venue_id).first().id,
    "name": Venue.query.filter_by(id=venue_id).first().name,
    "address": Venue.query.filter_by(id=venue_id).first().address,
    "city": Venue.query.filter_by(id=venue_id).first().city,
    "state": Venue.query.filter_by(id=venue_id).first().state,
    "phone": Venue.query.filter_by(id=venue_id).first().phone,
    "facebook_link": Venue.query.filter_by(id=venue_id).first().facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows":past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  venue = Venue()

  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.genres = request.form.getlist('genres')
  venue.address = request.form['address']
  venue.facebook_link = request.form['facebook_link']

  try:
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Venue ' +
      request.form['name'] + ' Could not be listed!')
    else:
      flash('Venue ' + request.form['name'] +
      ' was successfully listed!')
  return render_template('pages/home.html')

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
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  s_input = request.form.get('search_term')
  s_input ='%' + s_input + '%'
  artists = Artist.query.filter(Artist.name.ilike(s_input)).all()
  artist_count = Artist.query.filter(Artist.name.ilike(s_input)).count()

  data_list = []
  for artist in artists:
    data_list_temp= {
      "id" : artist.id,
      "name": artist.name
    }
    data_list.append(data_list_temp)

  response={
    "count": artist_count,
    "data": data_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  upcoming_shows_count = db.session.query(Venue).join(Show).filter_by(artist_id = artist_id).filter(Show.start_time>now).count()
  past_shows_count = db.session.query(Venue).join(Show).filter_by(artist_id = artist_id).filter(Show.start_time<now).count()
  past_shows = db.session.query(Show.start_time,Venue.id,Venue.name).join(Show).filter_by(artist_id  = artist_id).filter(Show.start_time<now).all()
  past_shows_list = []
  for past_show in past_shows:
    time = past_show[0]
    venue_id = past_show[1]
    venue_name = past_show[2]
    past_shows_list_temp = {
      "start_time" : time.strftime('%c'),
      "venue_id" : venue_id,
      "venue_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "venue_name" : venue_name
    }
    past_shows_list.append(past_shows_list_temp)
  
  upcoming_shows = db.session.query(Show.start_time,Venue.id,Venue.name).join(Show).filter_by(artist_id  = artist_id).filter(Show.start_time>now).all()
  upcoming_shows_list = []
  for upcoming_show in upcoming_shows:
    time = upcoming_show[0]
    venue_id = upcoming_show[1]
    venue_name = upcoming_show[2]
    upcoming_shows_list_temp = {
      "start_time" : time.strftime('%c'),
      "venue_id" : venue_id,
      "venue_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "venue_name" : venue_name
    }
    upcoming_shows_list.append(upcoming_shows_list_temp)

  
  data = {
    "id": artist_id,
    "name": Artist.query.filter_by(id=artist_id).first().name,
    "city": Artist.query.filter_by(id=artist_id).first().city,
    "state": Artist.query.filter_by(id=artist_id).first().state,
    "phone": Artist.query.filter_by(id=artist_id).first().phone,
    "genres": Artist.query.filter_by(id=artist_id).first().genres,
    "facebook_link": Artist.query.filter_by(id=artist_id).first().facebook_link,
    "seeking_venue": True,
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows" : past_shows_list,
    "upcoming_shows": upcoming_shows_list,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_by_id = Artist.query.filter_by(id=artist_id).first()
  artist = {
    "id": artist_id,
    "name": Artist.query.filter_by(id=artist_id).first().name,
  }
  form.city.data = artist_by_id.city
  form.name.data = artist_by_id.name
  form.state.data = artist_by_id.state
  form.phone.data = artist_by_id.phone
  form.genres.data = artist_by_id.genres
  form.facebook_link.data = artist_by_id.facebook_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False
  artist = Artist.query.filter_by(id=artist_id).first()

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form.getlist('genres')
  artist.facebook_link = request.form['facebook_link']

  try:
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Artist ' +
      request.form['name'] + ' Could not be listed!')
    else:
      flash('Artist ' + request.form['name'] +
      ' was successfully listed!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_by_id = Venue.query.filter_by(id=venue_id).first()
  venue = {
    "id": venue_id,
    "name": Venue.query.filter_by(id=venue_id).first().name,
  }
  form.city.data = venue_by_id.city
  form.name.data = venue_by_id.name
  form.state.data = venue_by_id.state
  form.phone.data = venue_by_id.phone
  form.facebook_link.data = venue_by_id.facebook_link
  form.address.data = venue_by_id.address

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.filter_by(id=venue_id).first()

  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.genres = request.form.getlist('genres')
  venue.address = request.form['address']
  venue.facebook_link = request.form['facebook_link']

  try:
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Venue ' +
      request.form['name'] + ' Could not be listed!')
    else:
      flash('Venue ' + request.form['name'] +
      ' was successfully listed!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  artist = Artist()

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form.getlist('genres')
  artist.facebook_link = request.form['facebook_link']

  try:
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Artist ' +
      request.form['name'] + ' Could not be listed!')
    else:
      flash('Artist ' + request.form['name'] +
      ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()

  data = []
  for show in shows:
    data_temp={
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": show.start_time.strftime('%c')
    }
  
    data.append(data_temp)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  show = Show()
  show.venue_id = request.form['venue_id']
  show.artist_id = request.form['artist_id']
  show.start_time = request.form['start_time']

  try:
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Show could not be listed!')
    else:
      flash('Show was successfully listed!')
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
