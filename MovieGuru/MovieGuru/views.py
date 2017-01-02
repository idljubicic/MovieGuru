 # -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template
from MovieGuru import app


from flask import url_for, request, session, redirect
from flask_oauth import OAuth
from pymongo import MongoClient
from fbutils import *
from dbutils import *
from operator import itemgetter

#----------------------------------------
# facebook authentication
#----------------------------------------


FACEBOOK_APP_ID = '381999122133791'
FACEBOOK_APP_SECRET = '434e56f2fdf6c437d2e029e4c3582da2'

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': ('public_profile', 'email, user_likes')}
)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('home')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    return redirect(next_url)

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('home'))

@app.route('/')
@app.route('/home')
@app.route('/trending')
def home():
    """Renders the home page."""
    client = MongoClient("mongodb://drumre_projekt:drumre123@ds119508.mlab.com:19508/drumre_projekt")
    db = client.get_database('drumre_projekt')
    coll = db.get_collection('tmdb')
    
    # find trending movies
    trending_movies = find_trending_movies(coll) 
   
    # gets the movie data from facebook for active user
    if session.get('logged_in') == True:
        user_id = get_user_id(facebook)
        movies = get_user_movie_data(session['facebook_token'][0])           
        save_user_liked_movies(user_id, movies, db.get_collection('tmdb'), db.get_collection('fb_data')) # save liked movie data for each new user
        
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        trending_movies=trending_movies
    )

@app.route('/movie/<string:imdb_id>')
def get_movie(imdb_id):
    """Renders the specific movie detail view."""
    client = MongoClient("mongodb://drumre_projekt:drumre123@ds119508.mlab.com:19508/drumre_projekt")
    db = client.get_database('drumre_projekt')
    coll = db.get_collection('tmdb')
        
    movie = get_movie_by_imdb_id(coll, imdb_id)
    poster_path = 'https://image.tmdb.org/t/p/w300_and_h450_bestv2' + str(movie['tmdb_poster_path'])

    return render_template('detail.html', poster_path = poster_path, movie = movie, year=datetime.now().year)

@app.route('/recommend')
def recommend():
    """Redners the movie recommendations for active user."""
    


    return render_template(
        'index.html',
        title='Recommendation Page',
        year=datetime.now().year,
    )

@app.route('/profile')
def profile():
    """Redners the user profile data."""
    if session.get('logged_in') == True:
        user_id = get_user_id(facebook)
        user_data = get_user_data(facebook)

        client = MongoClient("mongodb://drumre_projekt:drumre123@ds119508.mlab.com:19508/drumre_projekt")
        db = client.get_database('drumre_projekt')
        coll = db.get_collection('fb_data')
        movies = get_saved_movie_data(user_id, coll)
        genres = get_user_favourite_genres(user_id, coll)
        bla = True
    return render_template(
        'profile.html',
        title='Profile Page',
        user_data = user_data,
        movies = movies,
        genres = genres,
        itemgetter = itemgetter,
        year=datetime.now().year,
    )