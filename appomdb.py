import streamlit as st
import requests

# 🔑 OMDb API Key
OMDB_API_KEY = "1e0366ab"

# -------------------------------------------------
# Helper: Fetch info from OMDb
def get_movie_info(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return {
                "Title": data.get("Title"),
                "Year": data.get("Year"),
                "Genre": data.get("Genre"),
                "Plot": data.get("Plot"),
                "Poster": data.get("Poster"),
                "IMDB Rating": data.get("imdbRating")
            }
    return None

# -------------------------------------------------
# Streamlit UI
st.set_page_config(page_title="OMDb Movie Info", layout="wide")
st.title("🎬 Movie Info Finder (OMDb)")

query = st.text_input("Enter movie title:")

if query:
    if st.button("Get Info"):
        info = get_movie_info(query)
        if info:
            col1, col2 = st.columns([1, 3])
            with col1:
                if info["Poster"] and info["Poster"] != "N/A":
                    st.image(info["Poster"], width=250)
            with col2:
                st.markdown(f"**Title:** {info['Title']}")
                st.markdown(f"**Year:** {info['Year']}")
                st.markdown(f"**Genre:** {info['Genre']}")
                st.markdown(f"**IMDb Rating:** {info['IMDB Rating']}")
                st.markdown(f"**Plot:** {info['Plot']}")
        else:
            st.error("Movie not found in OMDb.")
