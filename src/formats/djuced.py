import sqlite3
import structs
from formats._djuced import (
    create_indices,
    create_tables,
    get_starts,
    get_cues,
    get_tracks,
    get_playlist_tracks,
    get_playlists,
    get_samples,
    insert_playlists,
    insert_samples,
    insert_tracks,
    insert_version_info
)


def parse_db(fname: str) -> structs.Library:
    """Parse the DJUCED database and return the created library.
    
    Some database fields are ignored as we don't know their use:
    
    - trackBeats.timesignature
    - tracks.smart_advisor
    - tracks.max_val_gain
    - tracks.rating
    - tracks.danceability
    - tracks.scores
    
    Other data that is discarded as its use is unknown or not applicable
    to other programs:
    
    - Cues with numbers >= 1000
    - Party playlists
    - Recordings
    - tblAdmin, tblFolderScan
    
    :param fname: The file name of the DJUCED database to read.
    """
    conn = sqlite3.connect(fname)
    cursor = conn.cursor()

    starts = get_starts(cursor)

    cues, hot_cues = get_cues(cursor)

    tracks, track_ids = get_tracks(cursor, starts, hot_cues, cues)

    playlist_track_ids = get_playlist_tracks(cursor, track_ids)

    playlists = get_playlists(cursor, playlist_track_ids)

    samples = get_samples(cursor)
    
    conn.close()

    return structs.Library(tracks, playlists, samples)


def write_db(fname: str, library: structs.Library):
    # implicitly create db if it doesn't exist
    conn = sqlite3.connect(fname)
    cursor = conn.cursor()

    create_tables(cursor)

    insert_samples(conn, cursor, library.samples)

    insert_tracks(conn, cursor, library.tracks)

    insert_playlists(conn, cursor, library)

    insert_version_info(conn, cursor)

    create_indices(cursor)
    
    conn.close()
