# Qobuz LastFM Downloader
This is a python app that runs every X hours to download albums that have been scrobbled to your lastfm account.
It uses Qobuz to download the albums.

Docker: rgallione/qobuz-lastfm-downloader:latest
Docker Hub Link: https://hub.docker.com/r/rgallione/qobuz-lastfm-downloader

## Configuration
You will need to handle a few configuration items for this docker to run properly.

### Directory Linking
The app uses two main directories:
- /downloads: The location of music downloaded
- /config: The location of the database

You will need to mount a host directory to these locations in Docker. 

### Environment Variables
There are a few environment variables that need to be set to run the docker.
```
QOBUZ_EMAIL=
QOBUZ_PASSWORD=
QUALITY=27
LASTFM_USERNAME=
RUN_EVERY_X_HOURS=1
```

- QOBUZ_EMAIL: Your Qobuz email address
- QOBUZ_PASSWORD: Your Qobuz password
- QUALITY: Optional, leave at 27 for the highest quality available
- LASTFM_UERNAME: Your LastFM username
- RUN_EVERY_X_HOURS: Optional, set to how often you want the downloader to check lastfm and run in hours



## LASTFM
You will need to create a https://last.fm account and setup a scrobbler for this to work. You can learn how to setup a qobuz scrobbler here: https://support.last.fm/t/qobuz-scrobbling/2876

This basically syncs everything you listen to on Qobuz to LastFM. This allows the script to pull the albums you've listened to in real-time so it can download them.

## Questions
Reach out to @jeremywade1337 on Telegram if you have any questions 

## Terms of Use
This project was intended for educational purposes only. I am not responsible for how you use this project.
