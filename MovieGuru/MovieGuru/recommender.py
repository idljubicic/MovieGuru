from __future__ import division
import re
from datetime import date
import pymongo
from operator import itemgetter


IMDB_MAX_SCORE = 10.0
METACRITIC_MAX_SCORE = 100
ROTTEN_TOMATOES_MAX_SCORE = 100
TMDB_SCORE_MAX = 10

# recommend movies based on all criteria: favourite genres, actors, directors, score, revenue, friend likes...
def recommend_total_criteria(coll, fav_movies, genres, actors, directors):
    similarity_d = dict()
    movies_all = coll.find({})
    TMDB_POPULARITY_MAX = coll.find({}).sort("tmdb_popularity", pymongo.DESCENDING).limit(1)[0]['tmdb_popularity']

    for movie in movies_all:
        if movie['imdb_id'] in fav_movies:
            continue
        try:
            similarity_rating = calculate_rating(movie, TMDB_POPULARITY_MAX) + calculate_actor_rating(movie, actors) + \
                     calculate_director_rating(movie['crew'], directors) + calculate_genre_rating(movie, genres) + calculate_year_rating(movie)
        except: # if movie has missing data
            similarity_rating = 0
        similarity_d[movie['imdb_id']] = similarity_rating
    
    recommended_movies = list()
    for k, v in sorted(similarity_d.items(), key=itemgetter(1), reverse=True):
        recommended_movies.append(coll.find_one({"imdb_id" : k}))
        if len(recommended_movies) == 20: # recommend n movies
            break
    return recommended_movies # return n recommended movies

# calculate normalized rating for every movie
def calculate_rating(movie, TMDB_POPULARITY_MAX):
    return ( float(movie['tmdb_popularity']) / TMDB_POPULARITY_MAX + float(movie['tmdb_vote_average']) / TMDB_SCORE_MAX \
            + float(movie['imdbRating']) / IMDB_MAX_SCORE + float(movie['tomatoMeter']) / ROTTEN_TOMATOES_MAX_SCORE \
            + float(movie['metascore']) / ROTTEN_TOMATOES_MAX_SCORE + float(movie['tomatoUserMeter']) / ROTTEN_TOMATOES_MAX_SCORE) / 3

# calculate favourite actors score
def calculate_actor_rating(movie, actors):
    actor_score = 0
    for actor in movie['cast']:
        actor_name = re.sub(r'\W+', ' ', actor['name'])      
        if actor_name in dict(actors):
            actor_score += actors[actor_name]
    
    if actor_score > 0:
        return 2 - 2 / actor_score
    else:
        return 0 

# calculate director rating for every movie
def calculate_director_rating(movie_directors, directors):
    d = False
    for director in movie_directors:
        director_name = re.sub(r'\W+', ' ', director['name'])      
        if director_name in dict(directors):
            d = True

    if d == True:
        return 1
    else:
        return 0

# calculate genre rating for every movie
def calculate_genre_rating(movie, genres):
    num_of_genres = 0
    for genre in movie['genres']:
        if genre in dict(genres):
            num_of_genres += 1
    
    if num_of_genres > 0:
        return 2 - 1 / num_of_genres
    else:
        return 0 

# calculate release year rating
def calculate_year_rating(movie):
    return ( 100 - (date.today().year - int(movie['release_date'].split('-')[0])) ) / 100

