import json
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyInterface:
    def __init__(self, config_path='config.json'):
        
        with open(config_path, 'rb') as f:
            config = json.load(f)
            
        client_credentials_manager = SpotifyClientCredentials(
            client_id=config['client_id'],
            client_secret=config['secret']
        )
        
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        self.user_id = config['user']

    def get_playlists_from_user(self, user_id: str = None) -> [dict]:
        if user_id is None:
            user_id = self.user_id
        return self._get_all_items(self.sp.user_playlists, user_id)

    def get_tracks_from_playlist(self, playlist_uri: str) -> [dict]:
        return self._get_all_items(self.sp.playlist_items, playlist_uri)

    def get_info_from_track(self, track: dict, include_analysis=True) -> dict[str, str]:
        info = dict()
        info['name'] = track['track']['name']
        info['artist'] = repr(tuple(a['name'] for a in track['track']['artists']))
        
        info['added_at'] = track['added_at']
        
        info['album'] = track['track']['album']['name']
        info['album_date'] = track['track']['album']['release_date']
        
        info['url'] = track['track']['external_urls']['spotify']
        info['uri'] = track['track']['uri']
        
        info['duration'] = track['track']['duration_ms']
        
        info['popularity'] = track['track']['popularity']
        # The popularity of the track. The value will be between 0 and 100, with 100 being the most popular.
        # The popularity of a track is a value between 0 and 100, with 100 being the most popular. The popularity is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent those plays are.
        # Generally speaking, songs that are being played a lot now will have a higher popularity than songs that were played a lot in the past. Duplicate tracks (e.g. the same track from a single and an album) are rated independently. Artist and album popularity is derived mathematically from track popularity. Note: the popularity value may lag actual popularity by a few days: the value is not updated in real time.
        
        if include_analysis:
            analysis = self.sp.audio_analysis(info['uri'])
            # The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
            info['analysis_tempo'] = analysis['track']['tempo']
            info['analysis_tempo_confidence'] = analysis['track']['tempo_confidence']
            # An estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of "3/4", to "7/4".
            info['analysis_time_signature'] = analysis['track']['time_signature']
            info['analysis_time_signature_confidence'] = analysis['track']['time_signature_confidence']
            # The key the track is in. Integers map to pitches using standard Pitch Class notation. E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1.
            info['analysis_key'] = analysis['track']['key']
            info['analysis_key_confidence'] = analysis['track']['key_confidence']
            # Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.
            info['analysis_mode'] = analysis['track']['mode']
            info['analysis_mode_confidence'] = analysis['track']['mode_confidence']
            
            features = self.sp.audio_features(info['uri'])[0]
            # see https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features
            info['features_danceability'] = features['danceability']
            # Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.
            info['features_energy'] = features['energy']
            # Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
            info['features_speechiness'] = features['speechiness']
            # Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.
            info['features_acousticness'] = features['acousticness']
            # A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.
            info['features_instrumentalness'] = features['instrumentalness']
            # Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
            info['features_liveness'] = features['liveness']
            # Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.
            info['features_loudness'] = features['loudness']
            # The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.
            info['features_valence'] = features['valence']
            # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).
        
        return info

    def get_df_from_playlist(self, playlist_uri: str, include_analysis=True) -> pd.DataFrame:
        # TODO columns sinnvoll sortieren?
        # TODO mit tqdm fortschritt anzeigen
        return pd.DataFrame.from_records(
            self.get_info_from_track(track, include_analysis)
            for track in self.get_tracks_from_playlist(playlist_uri)
        )
    
    # TODO see if I can reorder playlists by tempo using so.playlist_reorder_items

    @staticmethod
    def _get_all_items(getter_function, uri) -> list:
        # TODO besser generator zurückgeben statt list
        items = []
        offset = 0
        while True:
            response = getter_function(uri, offset=offset)
            new_items = response['items']
            items += new_items
            offset += response['limit']
            if response['next'] is None:
                break
        return items




