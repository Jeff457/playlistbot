import os
from playlist import spotify, youtube

if __name__ == "__main__":
    PLAYLIST_ID = os.getenv("PLAYLIST_ID")
    tracks = [
        "spotify:track:15kQGEy89K8deJcZVFEn0N",
        "spotify:track:2ARqIya5NAuvFVHSN3bL0m"
    ]
    results = spotify.playlist.add(
        playlist_id=PLAYLIST_ID,
        tracks=tracks
    )
    print(results)
