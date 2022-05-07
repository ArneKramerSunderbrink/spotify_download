from spotify_interface import SpotifyInterface

si = SpotifyInterface()

for playlist in si.get_playlists_from_user():

    # TODO print progress
    
    # TODO store this info somewhere?
    name = playlist['name']
    url = playlist['external_urls']['spotify']
    uri = playlist['uri']
    
    df = si.get_df_from_playlist(uri, include_analysis=False)
    
    df.to_csv('test.csv', index=False)  # TODO give a good name like playllistname_backupdate.csv...

