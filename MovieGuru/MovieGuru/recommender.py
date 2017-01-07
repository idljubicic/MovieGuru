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
    similarity_fav_genre = dict()
    similarity_fav_crew = dict()
    similarity_new_releases = dict()
    movies_all = coll.find({})
    TMDB_POPULARITY_MAX = coll.find({}).sort("tmdb_popularity", pymongo.DESCENDING).limit(1)[0]['tmdb_popularity']

    for movie in movies_all:
        if movie['imdb_id'] in fav_movies:
            continue
        try:
            if movie['title'] == "Silence":
                flag = True
            similarity_rating = calculate_rating(movie, TMDB_POPULARITY_MAX, 3) + calculate_actor_rating(movie, actors) + \
                     calculate_director_rating(movie['crew'], directors) + calculate_genre_rating(movie, genres) + calculate_year_rating(movie)
            similarity_d[movie['imdb_id']] = similarity_rating
        except:
            pass

        try:
            similarity_rating_new_releases = calculate_rating(movie, TMDB_POPULARITY_MAX, 3) + calculate_actor_rating(movie, actors) + \
                     calculate_director_rating(movie['crew'], directors) + calculate_genre_rating(movie, genres) + calculate_year_rating(movie)
            movie_release_year = int(movie['release_date'].split('-')[0])
            if movie_release_year < (date.today().year - 1):
                similarity_rating_new_releases = 0
            similarity_new_releases[movie['imdb_id']] = similarity_rating_new_releases
        except:
            pass

        try:
            similarity_rating_fav_genre = calculate_rating(movie, TMDB_POPULARITY_MAX, 2) + calculate_year_rating(movie)
            if genres[0][0] not in movie['genres']:
                similarity_rating_fav_genre = 0
            similarity_fav_genre[movie['imdb_id']] = similarity_rating_fav_genre
        except:
            pass

        try:
            similarity_rating_fav_crew = calculate_rating(movie, TMDB_POPULARITY_MAX, 3) + calculate_actor_rating(movie, actors[:2]) + \
                                        calculate_director_rating(movie['crew'], [directors[0]]) + calculate_year_rating(movie)
            similarity_fav_crew[movie['imdb_id']] = similarity_rating_fav_crew
        except: # if movie has missing data
            pass

    recommended_movies = list()
    recommended_movies_new_releases = list()
    recommended_movies_fav_genre = list()
    recommended_movies_fav_crew = list()

    for k, v in sorted(similarity_d.items(), key=itemgetter(1), reverse=True):
        recommended_movies.append(coll.find_one({"imdb_id" : k}))
        if len(recommended_movies) == 20: # recommend n movies
            break

    for k, v in sorted(similarity_new_releases.items(), key=itemgetter(1), reverse=True):
        recommended_movies_new_releases.append(coll.find_one({"imdb_id" : k}))
        if len(recommended_movies_new_releases) == 20: # recommend n newly released movies 
            break    

    for k, v in sorted(similarity_fav_genre.items(), key=itemgetter(1), reverse=True):
        recommended_movies_fav_genre.append(coll.find_one({"imdb_id" : k}))
        if len(recommended_movies_fav_genre) == 20: # recommend n movies based on favourite genre
            break

    for k, v in sorted(similarity_fav_crew.items(), key=itemgetter(1), reverse=True):
        recommended_movies_fav_crew.append(coll.find_one({"imdb_id" : k}))
        if len(recommended_movies_fav_crew) == 10: # recommend n movies based on favourite crew
            break

    return recommended_movies, recommended_movies_new_releases, recommended_movies_fav_genre, recommended_movies_fav_crew # return n recommended movies of all recommendation types

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# calculate normalized rating for every movie
def calculate_rating(movie, TMDB_POPULARITY_MAX, normalization_factor):
    rating = 0
    count = 0

    if is_number(movie['tmdb_popularity']):
        rating += float(movie['tmdb_popularity']) / TMDB_POPULARITY_MAX
        count += 1
    if is_number(movie['tmdb_vote_average']):
        rating += float(movie['tmdb_vote_average']) / TMDB_SCORE_MAX
        count += 1
    if is_number(movie['imdbRating']):
        rating += float(movie['imdbRating']) / IMDB_MAX_SCORE
        count += 1
    if is_number(movie['tomatoMeter']):
        rating += float(movie['tomatoMeter']) / ROTTEN_TOMATOES_MAX_SCORE
        count += 1
    if is_number(movie['metascore']):
        rating += float(movie['metascore']) / METACRITIC_MAX_SCORE
        count += 1
    if is_number(movie['tomatoUserMeter']):
        rating += float(movie['tomatoUserMeter']) / ROTTEN_TOMATOES_MAX_SCORE
        count += 1

    rating = (rating * 6) / count
    return rating / normalization_factor

# calculate favourite actors score
def calculate_actor_rating(movie, actors):
    try:
        actor_score = 0
        for actor in movie['cast']:
            actor_name = re.sub(r'\W+', ' ', actor['name'])      
            if actor_name in dict(actors):
                actor_score += dict(actors)[actor_name]
    
        if actor_score > 0:
            return 2 - 2 / actor_score
        else:
            return 0 
    except:
        return 0

# calculate director rating for every movie
def calculate_director_rating(movie_directors, directors):
    try:
        d = False
        for director in movie_directors:
            director_name = re.sub(r'\W+', ' ', director['name'])      
            if director_name in dict(directors):
                d = True

        if d == True:
            return 2
        else:
            return 0
    except:
        return 0

# calculate genre rating for every movie
def calculate_genre_rating(movie, genres):
    try:
        num_of_genres = 0
        for genre in movie['genres']:
            if genre in dict(genres):
                num_of_genres += 1
    
        if num_of_genres > 0:
            return 2 - 1 / num_of_genres
        else:
            return 0 
    except:
        return 0

def calculate_fav_genre_rating(movie,genre):
    try:
        if genre in movie['genres']:
            return 3
        else:
            return 0
    except:
        return 0

# calculate release year rating
def calculate_year_rating(movie):
    try:
        return ( 100 - (date.today().year - int(movie['release_date'].split('-')[0])) ) / 100
    except:
        return 0

