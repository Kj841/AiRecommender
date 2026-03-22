import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")

# -------------------------------
# Load data
# -------------------------------
@st.cache_data
def load_data():
    movies = pd.read_csv("movies_subset.csv")
    ratings = pd.read_csv("ratings_subset.csv")
    return movies, ratings

movies, ratings = load_data()

# -------------------------------
# Collaborative filtering matrix
# -------------------------------
@st.cache_data
def collab_matrix(ratings):
    matrix = ratings.pivot_table(index="userId", columns="movieId", values="rating", fill_value=0)
    sim_matrix = cosine_similarity(matrix.T)
    id_to_index = {mid: idx for idx, mid in enumerate(matrix.columns)}
    index_to_id = {idx: mid for idx, mid in enumerate(matrix.columns)}
    return matrix, sim_matrix, id_to_index, index_to_id

matrix, sim_matrix, id_to_index, index_to_id = collab_matrix(ratings)

# -------------------------------
# Genre content-based matrix
# -------------------------------
@st.cache_data
def genre_matrix(movies):
    movies_copy = movies.copy()
    movies_copy['genres'] = movies_copy['genres'].fillna('').str.replace('|', ' ')
    vec = CountVectorizer()
    genre_mat = vec.fit_transform(movies_copy['genres'])
    genre_sim = cosine_similarity(genre_mat)
    movieid_to_row = dict(zip(movies_copy['movieId'], movies_copy.index))
    return movies_copy, genre_sim, movieid_to_row

movies_copy, genre_sim, movieid_to_row = genre_matrix(movies)

# -------------------------------
# Functions
# -------------------------------
def search_movie(query, movies):
    return movies[movies['title'].str.lower().str.contains(query.lower(), na=False)]

def collab_recommend(movie_id, top_n=10):
    if movie_id not in id_to_index:
        return pd.DataFrame()
    idx = id_to_index[movie_id]
    sims = list(enumerate(sim_matrix[idx]))
    sims = sorted(sims, key=lambda x: x[1], reverse=True)
    sims = [s for s in sims if s[0] != idx][:top_n]
    rec_ids = [index_to_id[i] for i, _ in sims]
    scores = [s for _, s in sims]
    df = movies.set_index('movieId').loc[rec_ids].reset_index()
    df['score'] = scores
    df['year'] = df['title'].str.extract(r'\((\d{4})\)')
    return df

def genre_recommend(movie_id, top_n=10):
    if movie_id not in movieid_to_row:
        return pd.DataFrame()
    idx = movieid_to_row[movie_id]
    sims = list(enumerate(genre_sim[idx]))
    sims = sorted(sims, key=lambda x: x[1], reverse=True)
    sims = [s for s in sims if s[0] != idx][:top_n]
    rec_ids = [movies_copy.loc[i, 'movieId'] for i, _ in sims]
    scores = [s for _, s in sims]
    df = movies_copy.set_index('movieId').loc[rec_ids].reset_index()
    df['score'] = scores
    df['year'] = df['title'].str.extract(r'\((\d{4})\)')
    return df

# -------------------------------
# UI
# -------------------------------
st.markdown(
    """
    <h1 style="text-align:center; color:#FF4B4B;">🎬 Movie Recommender System 🍿</h1>
    """, unsafe_allow_html=True
)

st.sidebar.header("⚙️ Controls")
query = st.sidebar.text_input("🔎 Search for a movie")
top_n = st.sidebar.slider("Number of recommendations", 5, 20, 10)

st.sidebar.markdown(f"**📊 Dataset:** {len(movies)} movies, {len(ratings)} ratings")

if query:
    matched = search_movie(query, movies)
    if matched.empty:
        st.warning("No movie found.")
    else:
        selected = st.sidebar.selectbox("Select a movie:", matched['title'].tolist())
        if st.sidebar.button("✨ Show Recommendations"):
            movie_id = matched[matched['title'] == selected]['movieId'].values[0]
            
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🤝 Collaborative Recommendations")
                collab_df = collab_recommend(movie_id, top_n)[['title', 'year', 'genres', 'score']]
                st.dataframe(collab_df.style.background_gradient(cmap="Blues"))

            with col2:
                st.subheader("🎭 Genre-based Recommendations")
                genre_df = genre_recommend(movie_id, top_n)[['title', 'year', 'genres', 'score']]
                st.dataframe(genre_df.style.background_gradient(cmap="Greens"))
