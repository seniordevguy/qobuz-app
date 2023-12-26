import logging
import os
from qobuz_dl.core import QobuzDL
import schedule
import time
from dotenv import load_dotenv
import qobuz.api as qobuz_api
import qobuz as qobuz_cl

logging.basicConfig(level=logging.INFO)
load_dotenv()

qobuz_email = os.environ["QOBUZ_EMAIL"]
qobuz_pasword = os.environ["QOBUZ_PASSWORD"]
qobuz_app_id = os.environ["QOBUZ_APP_ID"]
music_directory = os.environ.get("MUSIC_DIRECTORY", "/downloads")
config_directory = os.environ.get("CONFIG_DIRECTORY", "/config")
quality = int(os.environ.get("QUALITY", 27))
run_every_x_hours = int(os.environ.get("RUN_EVERY_X_HOURS", 1))

# Or register your APP_ID and APP_SECRET
qobuz_api.register_app(qobuz_app_id)
qobuz_user = qobuz_cl.User(qobuz_email, qobuz_pasword)

qobuz = QobuzDL(
    directory=music_directory,
    quality=quality,
    downloads_db=os.path.join(config_directory, "db"),
    folder_format="{artist}/{artist} - {album}",
)

def get_user_favorites(user: qobuz_cl.User, fav_type, raw=False):
    '''
    Returns all user favorites

    Parameters
    ----------
    user: dict
        returned by qobuz.User
    fav_type: str
        favorites type: 'tracks', 'albums', 'artists'
    limi
    '''
    limit = 50
    offset = 0
    favorites = list()
    while True:
        favs = user.favorites_get(fav_type=fav_type, limit=limit, offset=offset, raw=raw)
        if raw:
            if len(favs[fav_type]["items"]) == 0:
                break
            for _f in favs[fav_type]["items"]:
                favorites.append(_f)
        else:
            if not favs:
                break
            favorites += favs
        offset += limit
    return favorites

def filter_existing_albums(albums):
    new_albums = []
    for album in albums:
        # Check if the path for the artist does NOT exist
        if not os.path.exists(os.path.join(music_directory, album['artist'], f"{album['artist']} - {album['title']}")):
            new_albums.append(album)
    return new_albums

def download_album_ids(qobuz: QobuzDL, album_ids):
    for album_id in album_ids:
        qobuz.download_from_id(album_id)

def job():
    try:
        # Initialize the Qobuz client
        qobuz.get_tokens()
        qobuz.initialize_client(qobuz_email, qobuz_pasword, qobuz.app_id, qobuz.secrets)

        # Retrieve favorite albums
        favorite_albums = get_user_favorites(qobuz_user, fav_type="albums", raw=True)

        print(f"Retrieved {len(favorite_albums)} albums...")

        # Parse albums
        parsed_albums = []
        for album in favorite_albums:
            album_id = album['id']
            album_info = {'id': album_id, 'title': album['title'], 'artist': album['artist']['name']}
            parsed_albums.append(album_info)

        # Filter new albums
        new_albums = filter_existing_albums(parsed_albums)
        print(f"Filtered Existing: Processing {len(new_albums)} albums...")

        # Download new albums
        new_album_ids = [album['id'] for album in new_albums]
        download_album_ids(qobuz, new_album_ids)

    except Exception as e:
        # Handle exceptions (e.g., network issues, data access problems)
        print(f"An error occurred: {e}")


schedule.every(run_every_x_hours).hours.do(job)
schedule.run_all()

while True:
    schedule.run_pending()
    time.sleep(1)
