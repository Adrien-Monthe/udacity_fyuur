from app import db
from forms import *


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column((db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    is_looking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', back_populates='venue', lazy=True)

    def future_shows(self):
        upcoming_shows = []

        for show in self.shows:
            if show.start_time > datetime.now():
                upcoming_shows.append(show)
        return upcoming_shows

    def past_shows(self):
        past_shows = []

        for show in self.shows:
            if show.start_time < datetime.now():
                past_shows.append(show)
        return past_shows

    def future_shows_with_join(self):
        future_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == self.id).filter(
            Show.start_time > datetime.now()).all()

        return future_shows_query

    def past_shows_with_join(self):
        past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == self.id).filter(
            Show.start_time < datetime.now()).all()

        return past_shows_query

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column((db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    is_looking_venues = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', back_populates='artist', lazy=True)

    def future_shows(self):
        upcoming_shows = []

        for show in self.shows:
            if show.start_time > datetime.now():
                upcoming_shows.append(show)
        return upcoming_shows

    def past_shows(self):
        past_shows = []

        for show in self.shows:
            if show.start_time < datetime.now():
                past_shows.append(show)
        return past_shows

    def future_shows_with_join(self):
        future_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == self.id).filter(
            Show.start_time > datetime.now()).all()

        return future_shows_query

    def past_shows_with_join(self):
        past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == self.id).filter(
            Show.start_time < datetime.now()).all()
        return past_shows_query

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'show'
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', back_populates='shows')
    artist = db.relationship('Artist', back_populates='shows')
