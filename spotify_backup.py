import os
import pandas as pd
from spotify_interface import SpotifyInterface
from datetime import datetime

DIRECTORY = 'backup'
if not os.path.exists(DIRECTORY):
    os.mkdir(DIRECTORY)

si = SpotifyInterface()

now = datetime.now().strftime('%Y-%m-%d')

playlist_data = []
for playlist in si.get_playlists_from_user():
    playlist_data.append(si.get_info_from_playlist(playlist))
    
    df = si.get_df_from_playlist(playlist, include_analysis=False, verbose=True)
    
    df.to_csv('{}/{}_{}.csv'.format(DIRECTORY, playlist['name'], now), index=False)

(
    pd.DataFrame
    .from_records(playlist_data, columns=si.PLAYLIST_COLUMNS)
    .to_csv('{}/playlists_{}.csv'.format(DIRECTORY, now), index=False)
)
