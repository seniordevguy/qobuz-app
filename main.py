import logging
import os
import schedule
import time
from threading import Thread, Event, Lock
from qobuz_dl.core import QobuzDL
from dotenv import load_dotenv
import qobuz.api as qobuz_api
import qobuz as qobuz_cl

logging.basicConfig(level=logging.INFO)
load_dotenv()

qobuz_email = os.environ["QOBUZ_EMAIL"]
qobuz_password = os.environ["QOBUZ_PASSWORD"]
music_directory = os.environ.get("MUSIC_DIRECTORY", "/downloads")
config_directory = os.environ.get("CONFIG_DIRECTORY", "/config")
quality = int(os.environ.get("QUALITY", 27))

# Use a threading.Lock for a safer thread locking mechanism
job_lock = Lock()

qobuz = QobuzDL(
    directory=music_directory,
    quality=quality,
    downloads_db=os.path.join(config_directory, "db"),
    folder_format="{artist}/{artist} - {album}",
)

def get_user_favorites(user: qobuz_cl.User, fav_type):
    '''
    Returns all user favorites

    Parameters
    ----------
    user: dict
        returned by qobuz.User
    fav_type: str
        favorites type: 'tracks', 'albums', 'artists'
    '''
    limit = 50
    offset = 0
    favorites = list()
    while True:
        favs = user.favorites_get(fav_type=fav_type, limit=limit, offset=offset)
        if not favs:
            break
        favorites += favs
        offset += limit
    return favorites

def download_albums(qobuz: QobuzDL, user: qobuz_cl.User, albums: list[qobuz_cl.Album]):
    successful_albums = []
    failure_albums = []
    for album in albums:
        try:
            # attempt to download the album
            qobuz.download_from_id(album.id)
            # if download is successful, remove from favorites
            user.favorites_del(album)
            successful_albums.append(album)
        except Exception as e:
            failure_albums.append(album)
            logging.error(f"An error occurred with album ID {album.id}: {e}")
    return successful_albums, failure_albums

def download_tracks(qobuz: QobuzDL, user: qobuz_cl.User, tracks: list[qobuz_cl.Track]):
    successful_tracks = []
    failure_tracks = []
    for track in tracks:
        try:
            # attempt to download the track
            qobuz.download_from_id(track.id, False)
            # if download is successful, remove from favorites
            user.favorites_del(track)
            successful_tracks.append(track)
        except Exception as e:
            failure_tracks.append(track)
            logging.error(f"An error occurred with track ID {track.id}: {e}")
    return successful_tracks, failure_tracks

def download_artists(qobuz: QobuzDL, user: qobuz_cl.User, artists: list[qobuz_cl.Artist]):
    successful_artists = []
    failure_artists = []
    for artist in artists:
        try:
            # attempt to download the artist
            qobuz.download_from_id(artist.id, False)
            # if download is successful, remove from favorites
            user.favorites_del(artist)
            successful_artists.append(artist)
        except Exception as e:
            failure_artists.append(artist)
            logging.error(f"An error occurred with artist ID {artist.id}: {e}")
    return successful_artists, failure_artists

def process_favorites():
    try:
        # initialize the Qobuz client
        qobuz.get_tokens()
        qobuz.initialize_client(qobuz_email, qobuz_password, qobuz.app_id, qobuz.secrets)

        # register your APP_ID
        qobuz_api.register_app(qobuz.app_id, qobuz.secrets)
        qobuz_user = qobuz_cl.User(qobuz_email, qobuz_password)

        # retrieve favorites
        favorite_albums = get_user_favorites(qobuz_user, fav_type="albums")
        favorite_tracks = get_user_favorites(qobuz_user, fav_type="tracks")
        favorite_artists = get_user_favorites(qobuz_user, fav_type="artists")

        logging.info(f"Processing {len(favorite_albums)} albums...")
        logging.info(f"Processing {len(favorite_tracks)} tracks...")
        logging.info(f"Processing {len(favorite_artists)} artists...")

        # download new favorites
        successful_tracks, failure_tracks = download_tracks(qobuz, qobuz_user, favorite_tracks)
        successful_albums, failure_albums = download_albums(qobuz, qobuz_user, favorite_albums)
        successful_artists, failure_artists = download_artists(qobuz, qobuz_user, favorite_artists)

        # log results
        logging.info(f"Successfully downloaded {len(successful_tracks)} tracks.")
        logging.info(f"Successfully downloaded {len(successful_albums)} albums.")
        logging.info(f"Successfully downloaded {len(successful_artists)} artists.")

        logging.warning(f"Failed to download {len(failure_tracks)} tracks.")
        logging.warning(f"Failed to download {len(failure_albums)} albums.")
        logging.warning(f"Failed to download {len(failure_artists)} artists.")
    except Exception as e:
        # handle exceptions (e.g., network issues, data access problems)
        logging.error(f"An error occurred: {e}")

def job():
    if job_lock.locked():
        logging.info("A job is already running. Exiting this schedule.")
        return

    # acquire the lock
    with job_lock:
        logging.info("Job started!")
        process_favorites()
        logging.info("Job finished!")

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each elapsed time interval."""
    cease_continuous_run = Event()

    class ScheduleThread(Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

# Schedule the job
schedule.every(30).minutes.do(job)

# Start the background thread
stop_run_continuously = run_continuously()
