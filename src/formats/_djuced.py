import structs
import sqlite3
from typing import List
import os
from datetime import datetime

COLORS = [
    structs.Color(0, "3924FB"),
    structs.Color(1, "69FFFE"),
    structs.Color(2, "2D8B15"),
    structs.Color(3, "59FD2F"),
    structs.Color(4, "EE0C19"),
    structs.Color(5, "F428FC"),
    structs.Color(6, "FFFFFF"),
    structs.Color(7, "F3AE29"),
    structs.Color(8, "FBFD37"),
]
"""The hardcoded DJUCED cue point colors.
"""


def get_starts(cursor: sqlite3.Cursor) -> dict:
    """Get the start position of each song from trackBeats.
    trackBeats.timesignature is discarded because we don't
    know what it does yet.

    :param cursor: The cursor to execute the query with.
    :returns: A dict of start times, indexed by the track file path.
    """
    starts_res = cursor.execute("SELECT * FROM trackBeats")
    start = starts_res.fetchone()
    starts = {}
    while start is not None:
        starts[start[1]] = start[2]
        start = starts_res.fetchone()
    return starts


def get_cues(cursor: sqlite3.Cursor) -> tuple[dict, dict]:
    """Get the cue points for each track from trackCues.
    Cue points are separated into cue 0 (hitting the "CUE" button)
    and the hot cues (1-8).
    Cues with numbers >= 1000 are discarded because we don't know their
    purpose yet.

    :param cursor: The cursor to execute the query with.
    :returns: A dict of Cues indexed by the track file path,
        another dict of lists of Hot Cues indexed by the track file path.
    """
    cues_res = cursor.execute("SELECT * FROM trackCues")
    cue = cues_res.fetchone()
    cues = {}
    hot_cues = {}
    while cue is not None:
        cue_struct = structs.CuePoint(
            name=cue[2],
            number=cue[3],
            pos=cue[4],
            color=COLORS[cue[6]],
            loopLength=cue[5],
        )
        if cue[3] == 0:
            cues[cue[1]] = cue_struct
        elif cue[3] < 1000:
            if cue[1] not in hot_cues:
                hot_cues[cue[1]] = []
            hot_cues[cue[1]].append(cue_struct)
        cue = cues_res.fetchone()
    return (cues, hot_cues)


def get_tracks(
    cursor: sqlite3.Cursor, starts: dict, hot_cues: dict, cues: dict
) -> tuple[List[structs.Track], dict]:
    """Get the tracks from tracks, as well as their IDs indexed by their
    file path.

    Information about tracks we don't know the meaning of is discarded.

    track start times, cues and hot cues are added to the Track models.

    :param cursor: The cursor to execute the query with.
    :param starts: The track start times, indexed by track file path.
    :param hot_cues: The tracs' hot cues, indexed by track file path.
    :param cues: The tracks' cue points, indexed by track file path.
    :returns: A list of tracks
        as well as a dict of track IDs indexed by the track file path.
    """
    tracks_res = cursor.execute("SELECT * FROM tracks")
    track = tracks_res.fetchone()
    tracks = []
    track_ids = {}
    while track is not None:
        track_ids[track[16]] = track[0]
        tracks.append(
            structs.Track(
                id=track[0],
                album=track[1],
                albumartist=track[2],
                artist=track[3],
                bitrate=track[4],
                comment=track[5],
                composer=track[6],
                cover_filepath=track[7],  # TODO test
                title=track[8],
                bpm=track[10],
                tracknumber=track[12],
                fname=track[16],
                first_beat_position=starts[track[16]] if track[16] in starts else 0,
                hot_cues=hot_cues[track[16]] if track[16] in hot_cues else [],
                cue=cues[track[16]] if track[16] in cues else None,
                key=int(track[18]) if track[18] != "" else 0,
                genre=track[19],
                filesize=track[20],
                length=int(track[21]) if track[21] != "" else None,
                last_modified=track[23],
                # just say -01-01, we don't know the actual date
                release_date=str(track[24]) + "-01-01",
                play_count=track[25],
                first_played=track[26],
                last_played=track[27],
                samplerate=track[32],
            )
        )
        track = tracks_res.fetchone()

    return (tracks, track_ids)


def get_playlist_tracks(cursor: sqlite3.Cursor, track_ids: dict) -> dict:
    """Get the IDs of all tracks in each playlist from playlists2.

    `track_ids` is used to map the track file path (which indexes it in playlist2)
    to its ID.

    :param cursor: The cursor to execute the query with.
    :param track_ids: The track IDs, indexed by the track file path.
    :returns: A dict of lists of track IDs, indexed by the playlist name.
    """
    playlist_tracks_res = cursor.execute("SELECT * FROM playlists2 WHERE type=3")
    playlist_track = playlist_tracks_res.fetchone()
    playlist_track_ids = {}
    while playlist_track is not None:
        if playlist_track[0] not in playlist_track_ids:
            playlist_track_ids[playlist_track[0]] = []
        playlist_track_ids[playlist_track[0]].append(track_ids[playlist_track[2]])
        playlist_track = playlist_tracks_res.fetchone()
    return playlist_track_ids


def get_playlists(
    cursor: sqlite3.Cursor, playlist_track_ids: dict
) -> List[structs.Playlist]:
    """Get the playlists from playlists2.

    `playlist_track_ids` are added to their respective playlists.

    :param cursor: The cursor to execute the query with.
    :param playlist_track_ids: Dict of Lists of track IDs, indexed by the playlist name.
    :returns: A list of playlists.
    """
    playlists_res = cursor.execute("SELECT * FROM playlists2 WHERE type=0")
    playlist = playlists_res.fetchone()
    playlists = []
    while playlist is not None:
        playlists.append(
            structs.Playlist(
                name=playlist[0],
                sort_order=playlist[3],
                track_ids=(
                    playlist_track_ids[playlist[0]]
                    if playlist[0] in playlist_track_ids
                    else []
                ),
            )
        )
        playlist = playlists_res.fetchone()
    return playlists


def get_samples(cursor: sqlite3.Cursor) -> List[structs.Sample]:
    """Get the samples from samples.

    :param cursor: The cursor to execute the query with.
    :returns: A list of samples.
    """
    samples_res = cursor.execute("SELECT * FROM samples")
    sample = samples_res.fetchone()
    samples = []
    while sample is not None:
        samples.append(structs.Sample(sample[1]))
        sample = samples_res.fetchone()
    return samples


def create_tables(cursor: sqlite3.Cursor):
    """Create the tables for the DJUCED DB.

    :param cursor: The cursor to execute the query with.
    """
    cursor.execute(
        (
            "CREATE TABLE playlists2("
            "name CHARACTER VARYING(100), "
            "path CHARACTER VARYING(1024), "
            "data CHARACTER VARYING(1024), "
            "order_in_list INTEGER, type INTEGER"
            ")"
        )
    )
    # we don't write to the recordings table
    cursor.execute(
        (
            "CREATE TABLE recordings("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "recordId CHARACTER VARYING(100) "
            ")"
        )
    )
    cursor.execute(
        (
            "CREATE TABLE samples("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "sampleId CHARACTER VARYING(255) "
            ")"
        )
    )
    # we don't write to tblAdmin and tblFolderScan
    cursor.execute(
        (
            "CREATE TABLE 'tblAdmin' ("
            "'key' TEXT PRIMARY KEY NOT NULL UNIQUE, "
            "'group' TEXT NOT NULL DEFAULT GENERAL, "
            "'keyval' TEXT"
            ")"
        )
    )
    cursor.execute(
        (
            "CREATE TABLE 'tblFolderScan' ("
            "Scan NUMERIC, "
            "FolderID INTEGER PRIMARY KEY, "
            "FolderPath TEXT, "
            "DisplayName TEXT"
            ")"
        )
    )
    cursor.execute(
        (
            "CREATE TABLE trackBeats("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "trackId CHARACTER VARYING(100), "
            "beatpos DECIMAL(5,1), "
            "timesignature INTEGER"
            ")"
        )
    )
    cursor.execute(
        (
            "CREATE TABLE trackCues("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "trackId CHARACTER VARYING(100), "
            "cuename CHARACTER VARYING(100), "
            "cuenumber INTEGER, "
            "cuepos DECIMAL(5,1), "
            "loopLength DECIMAL(5,1) DEFAULT 0, "
            "cueColor INTEGER"
            ")"
        )
    )
    cursor.execute(
        (
            "CREATE TABLE tracks("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "album CHARACTER VARYING(255), "
            "albumartist CHARACTER VARYING(255), "
            "artist CHARACTER VARYING(255), "
            "bitrate INTEGER, "
            "comment CHARACTER VARYING(100), "
            "composer CHARACTER VARYING(255), "
            "coverimage CHARACTER VARYING(255), "
            "title CHARACTER VARYING(255), "
            "smart_advisor INTEGER, "
            "bpm DECIMAL(5,1), "
            "max_val_gain FLOAT, "
            "tracknumber INTEGER, "
            "drive CHARACTER VARYING(16), "
            "filepath CHARACTER VARYING(1024), "
            "filename CHARACTER VARYING(255), "
            "absolutepath CHARACTER VARYING(1024), "
            "filetype CHARACTER VARYING(16), "
            "key INTEGER DEFAULT - 1, "
            "genre CHARACTER VARYING(100), "
            "filesize INTEGER, "
            "length DATETIME, "
            "rating INTEGER, "
            "filedate DATETIME, "
            "year INTEGER, "
            "playcount INTEGER, "
            "first_played DATETIME, "
            "last_played DATETIME, "
            "first_seen DATETIME, "
            "tags_read INTEGER, "
            "waveform BLOB, "
            "danceability FLOAT, "
            "samplerate INTEGER, "
            "stores CHARACTER VARYING(1024)"
            ")"
        )
    )


def create_indices(cursor: sqlite3.Cursor):
    """Create the indices for the DJUCED DB.

    :param cursor: The cursor to execute the query with.
    """
    cursor.execute("CREATE UNIQUE INDEX trackBeatsIndex ON trackBeats (trackId ASC)")
    cursor.execute("CREATE INDEX trackCuesIndex ON trackCues (trackId ASC)")
    cursor.execute("CREATE UNIQUE INDEX tracksIndex ON tracks (absolutepath ASC)")


def insert_samples(
    conn: sqlite3.Connection,
    cursor: sqlite3.Cursor,
    input_samples: List[structs.Sample],
):
    """Insert the given samples into the DB.

    :param conn: The connection to execute the query with.
    :param cursor: The cursor to execute the query with.
    :param samples: The samples to insert.
    """
    samples = []
    id = 1
    for sample in input_samples:
        samples.append((id, sample.fname))
        id += 1
    cursor.executemany("INSERT INTO samples VALUES(?, ?)", samples)
    conn.commit()


def insert_tracks(
    conn: sqlite3.Connection, cursor: sqlite3.Cursor, input_tracks: List[structs.Track]
):
    """Insert the given tracks into the DB.
    Also insert the corresponding trackBeats and trackCues entries.

    For columns with unknown meaning, default values corresponding to
    the most common values in the test data are used.

    :param conn: The connection to execute the query with.
    :param cursor: The cursor to execute the query with.
    :param tracks: The tracks to insert.
    """
    tracks = []
    track_beats = []
    track_beat_id = 1
    track_cue_id = 1
    for track in input_tracks:
        tracks.append(
            (
                track.id,
                track.album,
                track.albumartist,
                track.artist,
                track.bitrate,
                track.comment,
                track.composer,
                track.cover_filepath,
                track.title,
                track.bpm,
                track.tracknumber,
                track.fname[0:2],
                os.path.dirname(track.fname),
                os.path.basename(track.fname),
                track.fname,
                os.path.splitext(track.fname)[1],
                track.key,
                track.genre,
                track.filesize,
                track.length,
                track.last_modified,
                track.release_date.split("-")[0],
                track.play_count,
                track.first_played,
                track.last_played,
                datetime.today().strftime("%Y-%m-%dT%H:%M:%S"),
                track.samplerate,
            )
        )
        if track.cue is not None:
            cursor.execute(
                "INSERT INTO trackCues VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    track_cue_id,
                    track.fname,
                    track.cue.name,
                    track.cue.number,
                    track.cue.pos,
                    track.cue.loopLength,
                    4,
                ),
            )
            track_cue_id += 1
            conn.commit()
        if track.hot_cues:
            cues = []
            for cue in track.hot_cues:
                cues.append(
                    # color just defaults to zero because we can't map all colors
                    (
                        track_cue_id,
                        track.fname,
                        cue.name,
                        cue.number,
                        cue.pos,
                        cue.loopLength,
                        0,
                    )
                )
                track_cue_id += 1
            cursor.executemany(
                "INSERT INTO trackCues VALUES (?, ?, ?, ?, ?, ?, ?)", cues
            )
        track_beats.append(
            (
                track_beat_id,
                track.fname,
                (
                    track.first_beat_position
                    if track.first_beat_position is not None
                    else 0
                ),
                # 0 until we figure out what timesignature means
                0,
            )
        )
        track_beat_id += 1
    query_string = (
        "INSERT INTO tracks VALUES ("
        + ("?, " * 9)
        # smart_advisor is null because we don't know what it is
        # -9999.0 seems to be a placeholder value for max_val_gain
        + "NULL, ?, -9999.0, "
        + ("?, " * 10)
        # rating is 0 because we don't know what it is
        + "0, "
        + ("?, " * 6)
        # tags_read is 1 because we don't know what it is
        # waveform is NULL, DJUCED generates it anyway
        # danceability is 1.0 because we don't know how to calculate it
        # stores is NULL because we don't know what it is
        + "1, NULL, 1.0, ?, NULL)"
    )
    cursor.executemany(query_string, tracks)
    cursor.executemany("INSERT INTO trackBeats VALUES (?, ?, ?, ?)", track_beats)
    conn.commit()


def insert_playlists(
    conn: sqlite3.Connection, cursor: sqlite3.Cursor, library: structs.Library
):
    """Insert the given playlists into the DB.
    Also insert the corresponding playlist track entries.

    For columns with unknown meaning, default values corresponding to
    the most common values in the test data are used.

    :param conn: The connection to execute the query with.
    :param cursor: The cursor to execute the query with.
    :param library: The library with playlists/tracks to insert.
    """
    track_fnames_by_id = {}
    for track in library.tracks:
        track_fnames_by_id[track.id] = track.fname

    playlists = []
    playlist_tracks = []
    for playlist in library.playlists:
        # TODO: keep track sort order
        sort_order = 0
        # assume "#" for path until we figure out what it means
        playlists.append((playlist.name, "", playlist.sort_order))
        for track_id in playlist.track_ids:
            playlist_tracks.append(
                (playlist.name, track_fnames_by_id[track_id], sort_order)
            )
            sort_order += 1

    cursor.executemany("INSERT INTO playlists2 VALUES (?, '#', ?, ?, 0)", playlists)
    cursor.executemany(
        "INSERT INTO playlists2 VALUES (?, '#', ?, ?, 3)", playlist_tracks
    )
    conn.commit()


def insert_version_info(conn: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Insert the version info from the test data.

    :param conn: The connection to execute the query with.
    :param cursor: The cursor to execute the query with.
    """
    cursor.execute("INSERT INTO tblAdmin VALUES ('DB_VERSION', 'GENERAL', 0.059)")
    conn.commit()
