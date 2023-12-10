import logging
import os
from qobuz_dl.core import QobuzDL
import requests
import schedule
import time
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

qobuz_email = os.environ["QOBUZ_EMAIL"]
qobuz_pasword = os.environ["QOBUZ_PASSWORD"]
music_directory = os.environ.get("MUSIC_DIRECTORY", "downloads")
config_directory = os.environ.get("CONFIG_DIRECTORY", "config")
quality = int(os.environ.get("QUALITY", 27))
lastfm_api_key = os.environ.get("LASTFM_API_KEY", "b3d36aca59dd6dfa595c7034c8b0fa59")
lastfm_username = os.environ["LASTFM_USERNAME"]
run_every_x_hours = int(os.environ.get("RUN_EVERY_X_HOURS", 1))

qobuz = QobuzDL(
    directory=music_directory,
    quality=quality,
    downloads_db=os.path.join(config_directory, "db")
)

def fetch_all_top_albums(api_key, user):
    base_url = "http://ws.audioscrobbler.com/2.0/"
    albums = []

    params = {
        "method": "user.gettopalbums",
        "user": user,
        "api_key": api_key,
        "format": "json",
        "limit": 100
    }

    while True:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        # Add the albums from this page to your list
        albums.extend(data['topalbums']['album'])

        # Check if there's a next page
        if '@attr' in data['topalbums'] and int(data['topalbums']['@attr']['page']) < int(data['topalbums']['@attr']['totalPages']):
            params['page'] = int(data['topalbums']['@attr']['page']) + 1
        else:
            break

    formatted_albums = [f"{album['artist']['name']} - {album['name']}" for album in albums]
    return formatted_albums

def get_album_ids(qobuz: QobuzDL, albums):
    album_ids = []

    for album in albums:
        result = qobuz.search_by_type(album, "album", limit=1, lucky=True)
        if len(result) == 1:
            album_id = result[0].split('/')[-1]
            album_ids.append(album_id)

    return album_ids

def download_album_ids(qobuz: QobuzDL, album_ids):
    for album_id in album_ids:
        qobuz.download_from_id(album_id)

def job():
    qobuz.get_tokens()
    qobuz.initialize_client(qobuz_email, qobuz_pasword, qobuz.app_id, qobuz.secrets)
    albums = fetch_all_top_albums(lastfm_api_key, lastfm_username)
    ids = get_album_ids(qobuz, albums)
    download_album_ids(qobuz, ids)

schedule.every(run_every_x_hours).hours.do(job)
schedule.run_all()

while True:
    schedule.run_pending()
    time.sleep(1)