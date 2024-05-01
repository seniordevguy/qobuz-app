import logging
import os
import schedule
import time
from threading import Thread, Event
from qobuz_dl.core import QobuzDL
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

# this variable acts as a lock.
job_running = False

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
    limi
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
    successful_albums = list()
    failure_albums = list()
    for album in albums:
        try:
            # attempt to download the album
            qobuz.download_from_id(album.id)
            # if download is successful, remove from favorites
            user.favorites_del(album)
            # add to successful albums
            successful_albums.append(album)
        except Exception as e:
            # add to failure albums
            failure_albums.append(album)
            # handle any exceptions that occur
            print(f"An error occurred with album ID {album.id}: {e}")
    return successful_albums, failure_albums

def download_tracks(qobuz: QobuzDL, user: qobuz_cl.User, tracks: list[qobuz_cl.Track]):
    successful_tracks = list()
    failure_tracks = list()
    for track in tracks:
        try:
            # attempt to download the track
            qobuz.download_from_id(track.id, False)
            # if download is successful, remove from favorites
            user.favorites_del(track)
            # add to successful tracks
            successful_tracks.append(track)
        except Exception as e:
            # add to failure tracks
            failure_tracks.append(track)
            # handle any exceptions that occur
            print(f"An error occurred with track ID {track.id}: {e}")
    return successful_tracks, failure_tracks

def download_artists(qobuz: QobuzDL, user: qobuz_cl.User, artists: list[qobuz_cl.Artist]):
    successful_artists = list()
    failure_artists = list()
    for artist in artists:
        try:
            # attempt to download the artist
            qobuz.download_from_id(artist.id, False)
            # if download is successful, remove from favorites
            user.favorites_del(artist)
            # add to successful artists
            successful_artists.append(artist)
        except Exception as e:
            # add to failure artists
            failure_artists.append(artist)
            # handle any exceptions that occur
            print(f"An error occurred with artist ID {artist.id}: {e}")
    return successful_artists, failure_artists

def process_favorites():
    try:
        # initialize the Qobuz client
        qobuz.get_tokens()
        qobuz.initialize_client(qobuz_email, qobuz_pasword, qobuz.app_id, qobuz.secrets)

        # register your APP_ID
        qobuz_api.register_app(qobuz_app_id)
        qobuz_user = qobuz_cl.User(qobuz_email, qobuz_pasword)

        # retrieve favorites
        favorite_albums = get_user_favorites(qobuz_user, fav_type="albums")
        favorite_tracks = get_user_favorites(qobuz_user, fav_type="tracks")
        favorite_artists = get_user_favorites(qobuz_user, fav_type="artists")

        print(f"Processing {len(favorite_albums)} albums...")
        print(f"Processing {len(favorite_tracks)} tracks...")
        print(f"Processing {len(favorite_artists)} artists...")

        # download new favorites
        successful_tracks, failure_tracks = download_tracks(qobuz, qobuz_user, favorite_tracks)
        successful_albums, failue_albums = download_albums(qobuz, qobuz_user, favorite_albums)
        successful_artists, failure_artists = download_artists(qobuz, qobuz_user, favorite_artists)

        # print results
        print(f"Successfully downloaded {len(successful_tracks)} tracks.")
        print(f"Successfully downloaded {len(successful_albums)} albums.")
        print(f"Successfully downloaded {len(successful_artists)} artists.")

        print(f"Failed to download {len(failure_tracks)} tracks.")
        print(f"Failed to download {len(failue_albums)} albums.")
        print(f"Failed to download {len(failure_artists)} artists.")
    except Exception as e:
        # handle exceptions (e.g., network issues, data access problems)
        print(f"An error occurred: {e}")

def job():
    global job_running
    if job_running:
        print("A job is already running. Exiting this schedule.")
        return

    # set the lock
    job_running = True
    print("Job started!")
    
    # run job
    process_favorites()
    
    # release the lock
    job_running = False
    print("Job finished!")

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

schedule.every(3600).seconds.do(job)

# start the background thread
stop_run_continuously = run_continuously()