# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler

import re
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Venue, Artist, Show


# TODO: connect to a local postgresql database




# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    #       Getting the List of distinct combination of city and state in venue table
    data = []
    all_cities_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()

    # For each distinct combination of city and state we find the venues in it
    for distinct_city_state in all_cities_states:
        city_state_data = {
            "city": distinct_city_state[0],
            "state": distinct_city_state[1],
            "venues": []
        }
        city_state_venues = Venue.query.filter_by(city=distinct_city_state[0], state=distinct_city_state[1]).all()

        for venue in city_state_venues:
            city_state_data['venues'].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(venue.future_shows()),
            })
        print(city_state_data)
        data.append(city_state_data)

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".

    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_venue_name = request.form.get('search_term', '')
    search_venues_data = Venue.query.filter(Venue.name.ilike('%' + search_venue_name + '%')).all()
    response = {
        'count': len(search_venues_data),
        'data': []
    }

    for venue in search_venues_data:
        # Using Join for Future Shows

        response['data'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(venue.future_shows())
        })

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.filter_by(id=venue_id).first()
    data = []
    if venue:
        # Getting past and future shows with Join
        venue_future_shows = venue.future_shows_with_join()
        venue_past_shows = venue.past_shows_with_join()
        genres = []
        if venue.genres:
            genres = venue.genres.split(',')
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.is_looking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link if venue.image_link else "",
            "past_shows_count": len(venue_past_shows),
            "past_shows": [],
            "upcoming_shows_count": len(venue_future_shows),
            "upcoming_shows": [],
        }

        for show in venue_past_shows:
            artist = Artist.query.get(show.artist_id)
            data['past_shows'].append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
        for show in venue_future_shows:
            artist = Artist.query.get(show.artist_id)
            data['upcoming_shows'].append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })

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
    venue_form = VenueForm(request.form)
    # Regex to validate name
    if bool(re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})?', venue_form.name.data)):
        try:
            new_venue = Venue(
                name=venue_form.name.data,
                genres=','.join(venue_form.genres.data),
                address=venue_form.address.data,
                city=venue_form.city.data,
                state=venue_form.state.data,
                phone=venue_form.phone.data,
                facebook_link=venue_form.facebook_link.data,
                image_link=venue_form.image_link.data,
                website_link=venue_form.website_link.data,
                is_looking_talent=venue_form.seeking_talent.data,
                seeking_description=venue_form.seeking_description.data)

            db.session.add(new_venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        flash('An error occurred. Name Format is not Correct')


    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully Deleted!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be Deleted.')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    all_artists = Artist.query.all()
    data = []
    for artist in all_artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artists_by_name = request.form.get('search_term', '')
    search_artists_data = Artist.query.filter(Artist.name.ilike('%' + artists_by_name + '%')).all()
    response = {
        'count': len(search_artists_data),
        'data': []
    }

    for artist in search_artists_data:
        response['data'].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist.future_shows())
        })
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter_by(id=artist_id).first()
    data = []
    if artist:
        artist_future_shows = artist.future_shows()
        artist_past_shows = artist.past_shows()
        genres = []
        if artist.genres:
            genres = artist.genres.split(',')
            print(genres)
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "seeking_venue": artist.is_looking_venues,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "facebook_link": artist.facebook_link,
            "website": artist.website_link,
            "past_shows_count": len(artist_past_shows),
            "past_shows": [],
            "upcoming_shows_count": len(artist_future_shows),
            "upcoming_shows": [],
        }

        for show in artist_past_shows:
            venue = Venue.query.get(show.venue_id)
            data['past_shows'].append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            })
        for show in artist_future_shows:
            venue = Venue.query.get(show.venue_id)
            data['upcoming_shows'].append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            })
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    genres = []
    if artist.genres:
        genres = artist.genres.split(',')
    artist.genres = genres
    form = ArtistForm(obj=artist)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    if bool(re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})?', form.name.data)):
        try:
            artist = Artist.query.filter_by(id=artist_id).first()
            artist.name = form.name.data
            artist.genres = ','.join(form.genres.data)
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website_link = form.website_link.data
            artist.seeking_description = form.seeking_description.data
            artist.is_looking_venues = form.seeking_venue.data
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated!')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        flash('An error occurred. Name Format is not Correct')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    genres = []
    if venue.genres:
        genres = venue.genres.split(',')
    venue.genres = genres
    form = VenueForm(obj=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    regex = re.compile("^([a-zA-Z]{2,}\s[a-zA-Z]{1,}'?-?[a-zA-Z]{2,}\s?([a-zA-Z]{1,})?)", re.I)
    if bool(regex.match(form.name.data)):
        try:
            venue = Venue.query.filter_by(id=venue_id).first()
            venue.name = form.name.data
            venue.address = form.address.data
            venue.genres = ','.join(form.genres.data)
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website_link = form.website_link.data
            venue.is_looking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated!')
        finally:
            db.session.close()
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated!')
        flash('An error occurred. Name Format is not Correct')

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

    #if bool(re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})?', form.name.data)):
    try:
        artist = Artist(
            name=form.name.data,
            genres=','.join(form.genres.data),
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            is_looking_venues=form.seeking_venue.data,
            seeking_description=form.seeking_description.data)

        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
   # else:
    #    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    #    flash('An error occurred. Name Format is not Correct')

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    all_shows = Show.query.all()

    data = []
    for show in all_shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
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
    form = ShowForm(request.form)
    try:
        new_show = Show(
            artist_id=int(form.artist_id.data),
            venue_id=int(form.venue_id.data),
            start_time=form.start_time.data)

        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')

    finally:
        db.session.close()
    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
