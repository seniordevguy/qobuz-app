# Qobuz Downloader
This is a python app that runs continously to download favorites on your Qobuz account.

Docker: rgallione/qobuz-downloader:latest
Docker Hub Link: https://hub.docker.com/r/rgallione/qobuz-downloader

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
```

- QOBUZ_EMAIL: Your Qobuz email address
- QOBUZ_PASSWORD: Your Qobuz password
- QUALITY: Optional, leave at 27 for the highest quality available

## Questions
Reach out to @jeremywade1337 on Telegram if you have any questions 

## Terms of Use
This project was intended for educational purposes only. I am not responsible for how you use this project.
