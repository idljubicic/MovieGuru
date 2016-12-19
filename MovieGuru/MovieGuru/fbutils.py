import facebook as fb

# returns active user data
def get_user_data(fb):
    data = fb.get('/me').data
    if 'id' in data and 'name' in data:
        user_id = data['id']
        user_name = data['name']
    return (user_id,user_name)

# returns liked movie data from active user
def get_user_movie_data(fb_token):
    all_movies = list()
    graph = fb.GraphAPI(fb_token)
    movies = graph.get_connections('me','movies', limit=500)
    for movie in movies['data']:
        all_movies.append(movie) 
    while(True):
        if 'paging' in movies and 'after' in movies['paging']['cursors']:
            movies = graph.get_connections('me','movies',after=movies['paging']['cursors']['after'])
            for movie in movies['data']:
                all_movies.append(movie) 
        else:
            break

    return all_movies