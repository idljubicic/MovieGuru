 # -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template
from MovieGuru import app


from flask import url_for, request, session, redirect
from flask_oauth import OAuth
from pymongo import MongoClient
from fbutils import *
from dbutils import *


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
    request_token_params={'scope': ('email, user_likes')}
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
    
    posters_string = ur''
    for movie in trending_movies:
        # posters_string += '<div class="item" style="margin:3px"><img style=display:block;width:100%;height:auto" src="https://image.tmdb.org/t/p/w300_and_h450_bestv2' + str(movie['tmdb_poster_path']) + '" alt="' + str(movie['title']) + '"></div>'
        posters_string += '<div class="item"><img src="https://image.tmdb.org/t/p/w300_and_h450_bestv2' + str(movie['tmdb_poster_path']) + '" alt="' + str(movie['title']) + '"></div>'        


    # gets the movie data from facebook for active user
    if session.get('logged_in') == True:
        user_id, user_name = get_user_data(facebook)
        movies = get_user_movie_data(session['facebook_token'][0])           
        
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        posters=posters_string
    )
