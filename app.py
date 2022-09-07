# Imports
#----------------------------------------------------------------------------#
from html.entities import name2codepoint
from itertools import count
import json
import string
from types import CoroutineType
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_wtf import FlaskForm
import sys
from models import Artist, Venue, Show, db

import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#

# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  global venues
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue
    
  data = []#where we append the information for our data
  #grouping acoording to city and state as displayed above
  grouping_data= Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

 #iteration through each group thats is city and state
  for v in grouping_data:
    venue_data = []

  #get venues in each group/grouping the venues according to city and state
    venues = Venue.query.filter_by(state=v.state).filter_by(city=v.city).all()
      
#for each venue that was grouped above according to city and state 
    for venue in venues:
        upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()#checks shows that are set on a date later than today
#appending data to array venue_data then append that to array data with city and state
    venue_data.append({
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows": len(upcoming_shows)#num_upcoming_shows should be aggregated based on number of upcoming shows per venue
    })
    data.append({
      "city":v.city,
      "state":v.state,
      "venue": venue_data
    })
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venue_search = db.session.query(Venue).filter((Venue.name.ilike('%{}%'.format(search_term)))).all()
  response={
    "count": 0,
    "data": []
  }
  for venue in venue_search:
        search_data = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(venue.shows)
        }
  response["data"].append(search_data)
  response['count'] = len(response['data'])
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, 
  #data=Venue(name = "The Musical Hop",genres = ["Jazz", "Reggae", "Swing", "Classical", "Folk"],address = "1015 Folsom Street",city = "San Francisco",state =  "CA",phone = "123-123-1234",website = "https://www.themusicalhop.com",facebook_link =  "https://www.facebook.com/TheMusicalHop",seeking_talent = True,seeking_description = "We are on the lookout for a local artist to play every two weeks. Please call us.",image_link = "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60")
  venueby_id = Venue.query.filter(Venue.id==venue_id).first()#using venue_id
  #upcoming shows
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  if len(upcoming_shows) > 0:
      upcoming_show_data = []
    #each show
      for u in upcoming_shows:
          artist = Artist.query.filter(Artist.id == u.artist_id).first()
  
      upcoming_show_data.append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(u.start_time)

   })
      venueby_id.upcoming_shows = upcoming_show_data
      venueby_id.upcoming_shows_count = len(upcoming_show_data)
  #repeat above for past shows

  venueby_id = Venue.query.filter(Venue.id==venue_id).first()#using venue_id
  #upcoming shows
  past_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()#only this changes and variable name
  if len(past_shows) > 0:
    past_show_data = []
    #each show
    for u in past_shows:
      artist = Artist.query.filter(Artist.id == u.artist_id).first()
    past_show_data.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(u.start_time)

   })
    venueby_id.past_shows = past_show_data
    venueby_id.past_shows_count = len(past_show_data)
     
  return render_template('pages/show_venue.html', venue=venueby_id)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm( request.form)
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if not form:
    venue =Venue(
    id = form.id.data,
    name = form.name.data,
    city = form.city.data,
    state= form.state.data,
    phone = form.phone.data,
    website = form.website.data,
    facebook_link = form.city.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description =form.seeking_description.data,
    image_link=form.image_link.data
    )
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  if not venue:
        flash('No artist to delete')
        return redirect('/artists')
  if len(venue.shows) != 0:
        flash('You can\'t delete artists linked to some shows')
        return redirect('/artists/'+str(venue))
  db.session.delete(venue)
  db.session.commit()
  return redirect('/venues')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist = db.session.query(Artist).all()
  data = []
  for a in artist:
    data.append({
      "id":a.id,
      "name":a.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  global search_data
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(ilike does this)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artist_search = db.session.query(Artist).filter((Artist.name.ilike('%{}%'.format(search_term)))).all()
  response={
    "count": 0,
    "data": []
  }
  for artist in artist_search:
        search_data = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist.shows)
        }
  response["data"].append(search_data)
  response['count'] = len(response['data'])

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
   # Get venue
    data_artist = Artist.query.filter(Artist.id == artist_id).first()

    # Get the upcoming shows of this venue
    upcoming_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

    if len(upcoming_shows) > 0:
        data_upcoming_shows = []

        # Iterate over each upcoming show
        for upcoming_show in upcoming_shows:
            venue = Venue.query.filter(Venue.id == upcoming_show.venue_id).first()

            # Map upcoming shows
            data_upcoming_shows.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(past_show.start_time)
            })

        # Add shows data
        data_artist.upcoming_shows = data_upcoming_shows
        data_artist.upcoming_shows_count = len(data_upcoming_shows)

    # Get the past shows of this artist
    past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    if len(past_shows) > 0:
        data_past_shows = []

        # Iterate over each past show
        for past_show in past_shows:
            artist = Artist.query.filter(Artist.id == past_show.artist_id).first()

            # Map past shows
            data_past_shows.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(past_show.start_time),
            })

        # Add shows data
        data_artist.past_shows = data_past_shows
        data_artist.past_shows_count = len(data_past_shows)
    return render_template('pages/show_artist.html', artist=data_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  if not artist:
        flash('Venue not found!', 'error')
        return redirect('/venues')
   # TODO: populate form with values from venue with ID <venue_id>
  form = ArtistForm(request.form)
  form.name.data =  artist.name,
  form.city.data = artist.city,
  form.state.data = artist.state,
  form.phone.data = artist.phone,
  form.website_link.data = artist.website,
  form.city.data = artist.city,
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description,
  form.image_link.data = artist.image_link    
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  form = ArtistForm(request.form) 
  form.validate() # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist.name = form['name']
    artist.genres =form['genres']
    artist.city = form['city']
    artist.state= form['state']
    artist.phone = form['phone']
    artist.website = form['website_link']
    artist.facebook_link = form['city']
    artist.seeking_venue = form['seeking_venue']
    artist.seeking_description =form['seeking_description']
    artist.image_link=form['image_link']
    db.session.commit()
  except Exception:
          error = True
          db.session.rollback()
          print(sys.exc_info())
  finally:
          db.session.close()

  if error:
          flash('An error occurred. Artist '+ name + ' could not be updated.')
  if not error:
          flash('Artist '+ name + ' was successfully updated!','success')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).first()
  if not venue:
        flash('Venue not found!', 'error')
        return redirect('/venues')
   # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm(request.form)
  form.name.data =  venue.name,
  form.city.data = venue.city,
  form.state.data = venue.state,
  form.phone.data = venue.phone,
  form.website_link.data = venue.website,
  form.city.data = venue.city,
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description,
  form.image_link.data = venue.image_link    
      
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # Request data
  venue = Venue.query.filter(Venue.id == venue_id).first()

  
  form = VenueForm(request.form)
  venue.name = form['name']
  venue.genres=form['genres']
  venue.city = form['city']
  venue.state= form['state']
  venue.phone = form['phone']
  venue.website = form['website_link']
  venue.facebook_link = form['city']
  venue.seeking_talent = form['seeking_talent']
  venue.seeking_description =form['seeking_description']
  venue.image_link=form['image_link']
  # venue record with ID <venue_id> using the new attributes
  db.session.commit()
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
    form = ArtistForm(request.form)
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    # if not form :
    print(form.seeking_venue.data)


    artist = Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data
      )
      
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
  #     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #   else:
  #     flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  #   return render_template('pages/home.html')

#   on successful db insert, flash success
# flash('Artist ' + request.form['name'] + ' was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
#

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
   shows = db.session.query(Show).all()
   data = []
   for s in shows:
    artist = s.artist#used to get data from the Artist table that is the id of an artist
    venue = s.venue#used to get data from the Venue table id of a venue
    data.append({
      "venue_id":venue.id if  venue else None,
      "venue_name":venue.name if venue else None,
      "artist_id": artist.id if artist else None,
      "artist_name": artist.name if artist else None,
      "artist_image_link":artist.image_link if artist else None,
      "start_time": str(s.start_time)#make it a string so it can be displayed
    })
   return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    data = request.form
    show = Show()
    artist = db.session.query(Artist).filter_by(id=data['artist_id']).first()#filtering using the foreign key to find a venues existence;    
    # Check if artist to link exists
    if not artist:
        flash('Wrong user for the show!')
        return redirect('/shows/create')
    venue = db.session.query(Venue).filter_by(id=data['venue_id']).first()#filtering using the foreign key to find a venues existence
    # Check if Venue to link to the show exist
    if not venue:
        flash('Wrong venue for the show!')
        return redirect('/shows/create')
    try:
        show.start_time = dateutil.parser.parse(data['start_time'])
    except:
        flash('Wrong date for the show!')
        return redirect('/shows/create')
    show.artist_id = artist.id
    show.venue_id = venue.id
    db.session.add(show)
    db.session.commit()
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
