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
    title = re.sub(r'\([^)]*\)', '', title).strip()
    movie = coll.find_one({ "title" : title }) 
    return movie

# saves liked movie data from each facebook user
def save_user_liked_movies(user_id, movies, coll_tmdb, coll_fb_data):
    
    # data for user already exists
    if(coll_fb_data.find_one({ "user_id" : user_id }) != None):
        coll_fb_data.remove({ "user_id" : user_id})    


    liked_movies = list()
    genres = dict()
    actors = dict() 
    directors = dict()
    for movie in movies:
        mov = get_movie_by_title(coll_tmdb, movie['name'])
        if mov != None:
            liked_movies.append(mov['imdb_id']) 

            for genre in mov['genres']: # find favourite genres
                if genre not in genres:
                    genres.update({ genre : 0 })
                genres[genre] += 1
            
            for actor in mov['cast']: # find favourite actors
                actor_name = re.sub(r'\W+', ' ', actor['name'])             
                if actor_name not in actors:
                    actors.update({ actor_name : 0 })
                actors[actor_name] += 1
            
            for director in mov['crew']: # find favourite directors
                director_name = re.sub(r'\W+', ' ', director['name'])             
                if director_name not in directors:
                    directors.update({ director_name : 0 })
                directors[director_name] += 1          
            
    coll_fb_data.insert_one({ "user_id" : user_id, "liked_movies" : liked_movies, "genres" : genres, "actors" : actors, "directors": directors })
    return

# returns user liked movie ids from db
def get_saved_movie_ids(user_id, coll_fb_data):
    return coll_fb_data.find_one({ "user_id" : user_id })["liked_movies"]

# returns user liked movies from db
def get_saved_movie_data(user_id, coll_fb_data, coll_tmdb):
    return [get_movie_by_imdb_id(coll_tmdb, imdb_id) for imdb_id in get_saved_movie_ids(user_id, coll_fb_data)]
    

# returns user favourite genres from db
def get_user_favourite_genres(user_id, coll_fb_data):
    genres_d = coll_fb_data.find_one({ "user_id" : user_id })["genres"]
    genres_l = list()
    for k, v in sorted(genres_d.items(), key=itemgetter(1), reverse=True):
       genres_l.append((k,v))
    return genres_l[:5] # return n favourite genres

# returns user favourite actors from db
def get_user_favourite_actors(user_id, coll_fb_data):
    actors_d = coll_fb_data.find_one({ "user_id" : user_id })["actors"]
    actors_l = list()
    for k, v in sorted(actors_d.items(), key=itemgetter(1), reverse=True):
        actors_l.append((k,v))
    return actors_l[:20] # return n favourite actors

# returns user favourite directors from db
def get_user_favourite_directors(user_id, coll_fb_data):
    directors_d = coll_fb_data.find_one({ "user_id" : user_id })["directors"]
    directors_l = list()
    for k, v in sorted(directors_d.items(), key=itemgetter(1), reverse=True):
        directors_l.append((k,v))
    return directors_l[:5] # return n favourite directors    