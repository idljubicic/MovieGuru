import re
from datetime import date
import pymongo

def find_trending_movies(coll):
    regex_string = str(date.today().year) + "-*-*"
    regex = re.compile(regex_string)
    trending_movies = coll.find({ "release_date" : regex }).sort("revenue", pymongo.DESCENDING).limit(20)
    return trending_movies

