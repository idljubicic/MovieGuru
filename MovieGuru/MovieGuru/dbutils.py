import re
from datetime import date
import pymongo
from operator import itemgetter

# finds and returns current trending movies
def find_trending_movies(coll):
    regex_string = "(" + str(date.today().year) + "|" + str(date.today().year - 1) + ")" + "-*-*"
    regex = re.compile(regex_string)
    trending_movies = coll.find({ "release_date" : regex }).sort("revenue", pymongo.DESCENDING).limit(20)
    return trending_movies

# returns movie from database by given id 
def get_movie_by_imdb_id(coll, imdb_id):
    movie = coll.find_one({ "imdb_id" : imdb_id })
    return movie

# returns movie from database by given title
def get_movie_by_title(coll, title):
    movie = coll.find_one({ "title" : title }) 
    return movie

# saves liked movie data from each facebook user
def save_user_liked_movies(user_id, movies, coll_tmdb, coll_fb_data):
    
    # data for user already exists
    if(coll_fb_data.find_one({ "user_id" : user_id }) != None):
        return     


    liked_movies = list()
    genres = dict()
    for movie in movies:
        mov = get_movie_by_title(coll_tmdb, movie['name'])
        if mov != None:
            liked_movies.append(mov) 
            bla = mov['genres']
            for key, value in mov['genres'].iteritems():
                if value['name'] not in genres:
                    genres.update({ value['name'] : 0 })
                genres[value['name']] += 1
            
    coll_fb_data.insert_one({ "user_id" : user_id, "liked_movies" : liked_movies, "genres" : genres })
    return

# return user liked movie data from db
def get_saved_movie_data(user_id, coll_fb_data):
    return coll_fb_data.find_one({ "user_id" : user_id })["liked_movies"]

# return user favourite genres from db
def get_user_favourite_genres(user_id, coll_fb_data):
    genres_d = coll_fb_data.find_one({ "user_id" : user_id })["genres"]
    genres_l = list()
    for k, v in sorted(genres_d.items(), key=itemgetter(1), reverse=True):
       genres_l.append((k,v))
    return genres_l
    