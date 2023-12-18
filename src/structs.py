from dataclasses import dataclass, field
from typing import List


@dataclass
class Color:
    id: int
    hex_code: str


@dataclass
class CuePoint:
    pos: float
    name: str | None = None
    number: int | None = None
    color: Color | None = None
    loopLength: float = 0


@dataclass
class Track:
    title: str
    fname: str
    # database ID, for use with playlists later
    id: int | None = None

    # track metadata
    artist: str = ""
    album: str = ""
    albumartist: str = ""
    composer: str = ""
    tracknumber: int | None = None
    genre: str = ""
    release_date: str = ""
    cover_filepath: str = ""
    comment: str = ""

    # musical track info
    bpm: float = 90
    key: int = 0
    length: float | None = None
    first_beat_position: float | int = 0

    # dj info
    play_count: int = 0
    first_played: str = ""
    last_played: str = ""

    # file data
    bitrate: int | None = None
    bitdepth: int | None = None
    samplerate: int | None = None
    filesize: int | None = None
    last_modified: str = ""

    # aggregate data
    hot_cues: List[CuePoint] = field(default_factory=list)
    cue: CuePoint | None = None


@dataclass
class Playlist:
    name: str
    sort_order: int | None = None
    track_ids: List[int] = field(default_factory=list)


@dataclass
class Sample:
    fname: str


@dataclass
class Library:
    tracks: List[Track]
    playlists: List[Playlist]
    samples: List[Sample]
