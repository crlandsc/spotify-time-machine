import json
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

with open("token.txt", "r") as file:
    token = json.load(file)["access_token"]

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

user_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:\n")

billboard_full_url = f"{BILLBOARD_URL}{user_date}"

response = requests.get(billboard_full_url)
webpage_html = response.text
soup = BeautifulSoup(webpage_html, "html.parser")

song_titles = soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")
top_100_songs = []
for song_title in song_titles:
    text = song_title.getText()
    top_100_songs.append(text)

# print(top_100_songs)


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        client_id=CLIENT_ID,
        redirect_uri="http://example.com",
        client_secret=CLIENT_SECRET,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]
# print(user_id)

year_range_low = int(user_date[:4])-5
user_selected_year = int(user_date[:4])


uri_list = []
for song in top_100_songs:
    query = f"track:{song} year:{year_range_low}-{user_selected_year}"
    # print(query)

    spotify_song = sp.search(q=query, type='track')
    # print(spotify_song)

    try:
        uri = spotify_song["tracks"]["items"][0]["uri"]
        # print(uri)
        uri_list.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# print(uri_list)

playlist = sp.user_playlist_create(user=user_id, name=f"{user_selected_year} Billboard 100", public=False)


sp.playlist_add_items(playlist_id=playlist["id"], items=uri_list)

