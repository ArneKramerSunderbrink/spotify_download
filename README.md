# Spotify Download

Mainly for creating a csv backup of spotify playlists but also some fun analyses maybe...


## Init

Install requirements: 

    python3.9 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements_analysis.txt  # If you are interested in the analysis

Config:
- Go to https://developer.spotify.com/dashboard/applications
- Make an app
- Get the client ID and secret
- Get your username from https://www.spotify.com/de/account
- Make a file `config.json` containing:
    
      {
          "client_id": "*****",
          "secret": "*****",
          "user": "*****",
          "requests_timeout": 120
      }

## Backup

Create a backup folder with CSV files for all playlists of the user. Does not contain audio features from the
spotify analysers.

    . venv/bin/activate
    python spotify_backup.py

Note: The playlists need to have different names and none can be named "playlists". Else you have to change the file
names in `spotify_backup.py`, for example by changing `playlist['name']` to `playlist['id']`.

<!--- TODO make analysis notebook and mention it here --->

## References

Documentation of the Spotify Web API: https://developer.spotify.com/documentation/web-api/

Documentation on the spotipy library that wraps it: https://spotipy.readthedocs.io/en/2.19.0/
