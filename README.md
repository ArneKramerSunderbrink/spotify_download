# Spotify Download

Mainly for creating a csv backup of spotify playlists but also some fun analyses maybe...


## Init

- Install requirements.
  - python3.9 -m venv venv
  - . venv/bin/activate
  - pip install -r requirements.txt
- Config
  - go to https://developer.spotify.com/dashboard/applications
  - make an app
  - get the client ID and secret
  - get your username from https://www.spotify.com/de/account
  - Make a file `config.json` containing:
    
        {
            "client_id": "*****",
            "secret": "*****",
            "user": "*****",
            "requests_timeout": 120
        }


## References

Documentation of the Spotify Web API: https://developer.spotify.com/documentation/web-api/

Documentation on the spotipy library that wraps it: https://spotipy.readthedocs.io/en/2.19.0/
