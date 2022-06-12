import json
import logging
import pandas as pd

from spotipy import SpotifyException, Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from math import ceil
from tqdm import tqdm

from collections.abc import Iterator, Iterable
from typing import Union, Optional


class SpotifyInterface:
    MAX_FEATURES = 100
    PLAYLIST_COLUMNS = ['name', 'description', 'uri', 'url', 'owner_name', 'owner_uri']
    TRACK_COLUMNS_BASIC = [
        'added_at', 'uri', 'url', 'name', 'artist', 'album', 'album_date',
        'duration',
        # In ms
        'popularity'
        # The popularity of the track. The value will be between 0 and 100, with 100 being the most popular.
        # The popularity of a track is a value between 0 and 100, with 100 being the most popular. The popularity is
        # calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how
        # recent those plays are.
        # Generally speaking, songs that are being played a lot now will have a higher popularity than songs that were
        # played a lot in the past. Duplicate tracks (e.g. the same track from a single and an album) are rated
        # independently. Artist and album popularity is derived mathematically from track popularity. Note: the
        # popularity value may lag actual popularity by a few days: the value is not updated in real time.
    ]
    TRACK_COLUMNS_AUDIO_FEATURES = [
        # see https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features
        'tempo',
        # The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the
        # speed or pace of a given piece and derives directly from the average beat duration.
        'time_signature',
        # An estimated time signature. The time signature (meter) is a notational convention to specify how many
        # beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of
        # "3/4", to "7/4".
        'key',
        # The key the track is in. Integers map to pitches using standard Pitch Class notation. E.g. 0 = C,
        # 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1.
        'mode',
        # Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content
        # is derived. Major is represented by 1 and minor is 0.
        'danceability',
        # Danceability describes how suitable a track is for dancing based on a combination of musical elements
        # including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least
        # danceable and 1.0 is most danceable.
        'energy',
        # Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity.
        # Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a
        # Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic
        # range, perceived loudness, timbre, onset rate, and general entropy.
        'speechiness',
        # Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the
        # recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66
        # describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe
        # tracks that may contain both music and speech, either in sections or layered, including such cases as rap
        # music. Values below 0.33 most likely represent music and other non-speech-like tracks.
        'acousticness',
        # A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the
        # track is acoustic.
        'instrumentalness',
        # Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this
        # context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0,
        # the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent
        # instrumental tracks, but confidence is higher as the value approaches 1.0.
        'liveness',
        # Detects the presence of an audience in the recording. Higher liveness values represent an increased
        # probability that the track was performed live. A value above 0.8 provides strong likelihood that the
        # track is live.
        'loudness',
        # The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and
        # are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the
        # primary psychological correlate of physical strength (amplitude). Values typically range between -60 and
        # 0 db.
        'valence'
        # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high
        # valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more
        # negative (e.g. sad, depressed, angry).
    ]
    TRACK_COLUMNS = TRACK_COLUMNS_BASIC + TRACK_COLUMNS_AUDIO_FEATURES

    def __init__(self, config_path='config.json'):
        
        with open(config_path, 'rb') as f:
            config = json.load(f)
            
        client_credentials_manager = SpotifyClientCredentials(
            client_id=config['client_id'],
            client_secret=config['secret']
        )
        
        self.sp = Spotify(
            client_credentials_manager=client_credentials_manager,
            requests_timeout=config['requests_timeout']
        )
        
        self.user_id = config['user']

    def get_user_id_from_user(self, user: Union[str, dict] = None) -> str:
        """
        user: id, uri, or dict as returned by self.sp.user(id)
        """
        if user is None:
            return self.user_id
        elif type(user) == dict:
            return user['id']
        elif user.startswith('spotify:user:'):
            return user[len('spotify:user:'):]
        else:
            return user

    @staticmethod
    def get_playlist_uri_from_playlist(playlist: Union[str, dict]) -> str:
        """
        playlist: id, uri, or dict as returned by self.sp.playlist(uri)
        """
        if type(playlist) == dict:
            return playlist['uri']
        elif playlist.startswith('spotify:playlist:'):
            return playlist
        else:
            return 'spotify:playlist:' + playlist

    def get_playlist_from_playlist(self, playlist: Union[str, dict]) -> Optional[dict]:
        """
        playlist: id, uri, or dict as returned by self.sp.playlist(uri)
        """
        if type(playlist) == dict:
            return playlist
        else:
            try:
                return self.sp.playlist(playlist)
            except SpotifyException:
                logging.warning(f'Could not find playlist for uri {playlist}.')
                return None

    @staticmethod
    def get_track_uri_from_track(track: Union[str, dict]) -> str:
        """
        track: id, uri, or dict as returned by self.sp.track(uri)
        """
        if type(track) == dict:
            return track['uri']
        elif track.startswith('spotify:track:'):
            return track
        else:
            return 'spotify:track:' + track

    def get_track_from_track(self, track: Union[str, dict]) -> Optional[dict]:
        """
        track: id, uri, or dict as returned by self.sp.track(uri)
        """
        if type(track) == dict:
            return track
        else:
            try:
                return self.sp.track(track)
            except SpotifyException:
                logging.warning(f'Could not find track for uri {track}.')
                return None

    def get_playlists_from_user(self, user: Union[str, dict] = None) -> [dict]:
        """
        user: id, uri, or dict as returned by self.sp.user(id)
        """
        user_id = self.get_user_id_from_user(user)
        return self._get_all_items(self.sp.user_playlists, user_id)

    def get_tracks_from_playlist(self, playlist: Union[str, dict]) -> [dict]:
        """
        playlist: id, uri, or dict as returned by self.sp.playlist(uri)
        """
        playlist_uri = self.get_playlist_uri_from_playlist(playlist)
        return self._get_all_items(self.sp.playlist_items, playlist_uri)

    def get_info_from_playlist(self, playlist: Union[str, dict]) -> dict[str, str]:
        """
        playlist: id, uri, or dict as returned by self.sp.playlist(uri)
        """
        playlist = self.get_playlist_from_playlist(playlist)
        if playlist is None:
            return {key: None for key in self.PLAYLIST_COLUMNS}

        info = dict()
        info['name'] = playlist['name']
        info['description'] = playlist['description']
        info['uri'] = playlist['uri']
        info['url'] = playlist['external_urls'].get('spotify', None)
        info['owner_name'] = playlist['owner']['display_name']
        info['owner_uri'] = playlist['owner']['uri']

        return info

    def get_audio_features(self, tracks: Iterable[Union[str, dict]]) -> Iterator[dict]:
        """
        tracks: Sequence of ids, uris, or dicts as returned by self.sp.track(uri)
        """
        track_uris = [self.get_track_uri_from_track(track) for track in tracks]
        return (
            af
            for i in range(ceil(len(track_uris) / self.MAX_FEATURES))
            for af in self.sp.audio_features(track_uris[
                                                 i * self.MAX_FEATURES:
                                                 min((i + 1) * self.MAX_FEATURES, len(track_uris))
                                             ])
        )

    def get_info_from_track(self, track: Union[str, dict]) -> dict[str, str]:
        """
        track: id, uri, or dict as returned by self.sp.track(uri)
        """
        track = self.get_track_from_track(track)
        if track is None:
            return {key: None for key in self.TRACK_COLUMNS}

        info = dict()
        info['name'] = track['track']['name']
        info['artist'] = repr(tuple(a['name'] for a in track['track']['artists']))
        
        info['added_at'] = track['added_at']
        
        info['album'] = track['track']['album']['name']
        info['album_date'] = track['track']['album']['release_date']
        
        info['url'] = track['track']['external_urls'].get('spotify', None)
        info['uri'] = track['track']['uri']
        
        info['duration'] = track['track']['duration_ms']
        
        info['popularity'] = track['track']['popularity']
        
        return info

    def get_info_from_audio_features(self, audio_features: dict) -> dict:
        """
        audio_features: Of a single track as returned by self.sp.audio_features(track)[0]
        """
        return {
            key: audio_features[key] if audio_features is not None else None
            for key in self.TRACK_COLUMNS_AUDIO_FEATURES
        }

    def get_df_from_playlist(self, playlist: Union[str, dict], include_audio_features=True, verbose=True
                             ) -> pd.DataFrame:
        """
        playlist: id, uri, or dict as returned by self.sp.playlist(uri)
        """
        track_iterator = self.get_tracks_from_playlist(playlist)
        if verbose:
            playlist_name = self.get_info_from_playlist(playlist)['name']
            track_iterator = tqdm(
                track_iterator,
                unit=' tracks',
                desc='Retrieving tracks from playlist {}'.format(playlist_name)
            )

        df = pd.DataFrame.from_records(
            (
                self.get_info_from_track(track)
                for track in track_iterator
            ),
            columns=self.TRACK_COLUMNS_BASIC
        )

        df.dropna(subset=['uri'], inplace=True)  # drop rows from invalid URIs

        if include_audio_features:
            features_iterator = self.get_audio_features(df['uri'])

            if verbose:
                features_iterator = tqdm(
                    features_iterator,
                    unit=' tracks',
                    desc='Retrieving audio features from playlist {}'.format(playlist_name),
                    total=len(df)
                )

            df_features = pd.DataFrame.from_records(
                (self.get_info_from_audio_features(feature) for feature in features_iterator),
                columns=self.TRACK_COLUMNS_AUDIO_FEATURES
            )

            df = pd.concat((df, df_features), axis=1)

        return df
    
    # TODO see if I can reorder playlists by tempo using sp.playlist_reorder_items

    @staticmethod
    def _get_all_items(getter_function, uri) -> Iterator:
        offset = 0
        while True:
            response = getter_function(uri, offset=offset)
            new_items = response['items']
            for item in new_items:
                yield item
            offset += response['limit']
            if response['next'] is None:
                break
