from spotipy import Spotify, util, SpotifyException
from collections import Counter


# Spotify limits playlists to 10k songs
SONG_LIMIT = 1e4
SCOPE = "playlist-modify-public"


class SpotifyPlaylistException:
    pass


class SpotifyPlaylist:
    def __init__(self, *, user: str, client_id: str, client_secret: str,
                 redirect_uri: str, **kwargs):
        """Init SpotifyPlaylist.

        Args:
            user: A str representing the Spotify user id.
            client_id: A str representing the app client id.
            client_secret: A str representing the app client secret.
            redirect_uri: A str representing the app redirect URI.
        """
        # authenticates app to access user's data
        self._token = util.prompt_for_user_token(
            username=user,
            scope=SCOPE,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        self.user = user
        self.spotify = Spotify(auth=self._token)
        self.playlist_count = Counter()

    def remove_tracks(self, *, playlist_id: str, n_tracks: int, **kwargs):
        """Delete tracks from specified playlist if adding n_tracks exceeds SONG_LIMIT.

        Delete n tracks from the specified playlist if the size of the
        playlist + n_tracks exceeds SONG_LIMIT, where
        n = len(playlist) + n_tracks - SONG_LIMIT

        Also keeps track of the size of the playlist.

        Args:
            playlist_id: The playlist to add tracks to.
            n_tracks: The number of tracks to add.

        Raises:
            SpotifyPlaylistException: n_tracks exceeds SONG_LIMIT
        """
        playlist = self.spotify.user_playlist(
            user=self.user,
            playlist_id=playlist_id,
            fields="tracks,next,name"
        )
        tracks = playlist["tracks"]

        total_tracks = self.playlist_count[playlist_id] + n_tracks
        if total_tracks >= SONG_LIMIT:
            n = total_tracks - SONG_LIMIT

            # make sure we aren't trying to add too many tracks
            if n > self.playlist_count[playlist_id]:
                raise SpotifyPlaylistException(
                    f"{n_tracks} exceeds playlist song limit of {SONG_LIMIT}"
                )

            count = 0
            remove = []

            for item in tracks["items"]:
                if count >= n:
                    break
                remove.append(item["track"]["id"])
                count += 1

            # remove tracks from playlist
            self.spotify.user_playlist_remove_all_occurrences_of_tracks(
                user=self.user,
                playlist_id=playlist_id,
                tracks=remove
            )
        elif self.playlist_count[playlist_id] == 0:
            while True:
                # count songs in playlist
                self.playlist_count[playlist_id] += tracks["total"]

                if tracks["next"]:
                    tracks = self.spotify.next(tracks)
                else:
                    break

    def add_track(self, *, playlist_id: str, tracks: list, **kwargs):
        """Add tracks to specified playlist.

        Removes n tracks from the playlist iff the size of the playlist +
        len(tracks) exceeds SONG_LIMIT,
        where n = len(playlist) + len(tracks) - SONG_LIMIT.

        After ensuring the added tracks won't exceed SONG_LIMIT, add
        tracks to the playlist.

        Args:
            playlist_id: A str representing the playlist ID to modify.
            tracks: A list of track IDs to add to the specified playlist.

        Raises:
            SpotifyPlaylistException: For 4xx - 5xx HTTP response codes or
                if the number of tracks exceeds SONG_LIMIT.

        Returns:
            i'll check
        """
        # remove tracks if the size of the playlist will exceed SONG_LIMIT
        self.remove_tracks(playlist_id=playlist_id, n_tracks=len(tracks))

        try:
            # add tracks to the playlist
            results = self.spotify.user_playlist_add_tracks(
                user=self.user,
                playlist_id=playlist_id,
                tracks=tracks
            )

            # keep track of playlist song count
            self.playlist_count[playlist_id] += len(tracks)
            return results
        except SpotifyException as e:
            raise SpotifyPlaylistException(str(e))


if __name__ == "__main__":
    import os
    USER = os.getenv("USER")
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URL")
    PLAYLIST_ID = os.getenv("PLAYLIST_ID")

    spotify_playlist = SpotifyPlaylist(
        user=USER,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )
    tracks = [
        "spotify:track:15kQGEy89K8deJcZVFEn0N",
        "spotify:track:2ARqIya5NAuvFVHSN3bL0m"
    ]
    results = spotify_playlist.add_track(
        playlist_id=PLAYLIST_ID,
        tracks=tracks
    )
    print(results)
