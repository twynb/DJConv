import xml.sax.saxutils
import structs


def parse_db(fname: str):
    print("TODO")


def write_db(fname: str, library: structs.Library):
    with open(fname, "w+", encoding="utf8") as file:
        # begin xml
        file.write(
            '<?xml version="1.0" encoding="UTF-8" ?>'
            + '<DJ_PLAYLISTS Version="1.0.0">'
            + '<PRODUCT Name="rekordbox" Version="5.4.3" Company="Pioneer DJ" />'
        )
        # begin collection
        num_entries = len(library.tracks)
        file.write(f'<COLLECTION Entries="{num_entries}">\n')
        # write tracks
        for track in library.tracks:
            extension = track.fname.split(".")[-1]
            kind = "unknown"

            match extension:
                case "wav":
                    kind = "Wav-Datei"
                case "mp3":
                    kind = "Mp3-Datei"
            key = ""
            if track.key is not None:
                key_number = track.key % 12
                key = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"][
                    key_number
                ]
                if track.key >= 12:
                    key += "m"
            track_attrs = {
                "TrackID": track.id,
                "Name": track.title,
                "Artist": track.artist,
                "Composer": track.composer,
                "Album": track.album,
                "Genre": track.genre,
                "Kind": kind,
                "Size": track.filesize,
                "TotalTime": int(track.length) if track.length is not None else 0,
                "DiscNumber": 0,
                "TrackNumber": track.tracknumber
                if track.tracknumber is not None
                else 0,
                "Year": track.release_date.split("-")[0],
                "AverageBpm": _append_post_comma_zeroes(track.bpm),
                "DateAdded": track.last_modified,
                "BitRate": track.bitrate,
                "SampleRate": track.samplerate,
                "Comments": track.comment,
                "PlayCount": track.play_count,
                "Rating": 0,
                "Location": "file://localhost/" + track.fname,
                "Tonality": key,
            }
            track_xml_data = _serialize_dict_to_xml(track_attrs)

            file.write(f"<TRACK {track_xml_data}>\n")
            # write tempo
            tempo_attrs = {
                "Inizio": _append_post_comma_zeroes(track.first_beat_position),
                "Bpm": _append_post_comma_zeroes(track.bpm),
                "Metro": "4/4",
                "Battito": "1",
            }
            tempo_attrs_xml = _serialize_dict_to_xml(tempo_attrs)
            file.write(f"<TEMPO {tempo_attrs_xml} />")
            # write hot cues
            for cue in track.hot_cues:
                cue_attrs = {
                    "Name": cue.name,
                    "Type": 0,
                    "Start": _append_post_comma_zeroes(cue.pos),
                    "End": _append_post_comma_zeroes(
                        (cue.pos + cue.loopLength) if cue.loopLength != 0 else None
                    ),
                    "Num": cue.number - 1 if cue.number is not None else None,
                }
                cue_attrs_xml = _serialize_dict_to_xml(cue_attrs)
                file.write(f"<POSITION_MARK {cue_attrs_xml} />\n")
            file.write("</TRACK>")

        # end collection
        file.write(f"</COLLECTION>")
        # begin playlists
        file.write(f"<PLAYLISTS>\n")
        num_playlists = len(library.playlists)
        file.write(f'<NODE Type="0" Name="ROOT" Count="{num_playlists}">')
        # write each playlist
        for playlist in library.playlists:
            playlist_attrs = {
                "Type": 1,
                "Entries": len(playlist.track_ids),
                "KeyType": 0,
                "Name": playlist.name,
            }
            playlist_attrs_xml = _serialize_dict_to_xml(playlist_attrs)
            file.write(f"<NODE {playlist_attrs_xml}>\n")
            for id in playlist.track_ids:
                file.write(f'<TRACK Key="{id}" />')
            file.write(f"</NODE>")
        # end playlists and xml
        file.write(f"</NODE></PLAYLISTS></DJ_PLAYLISTS>")


def _serialize_dict_to_xml(input: dict) -> str:
    return " ".join(
        [
            (key + "=" + xml.sax.saxutils.quoteattr(str(value)))
            for key, value in input.items()
            if value is not None
        ]
    )


def _append_post_comma_zeroes(input):
    return (str(input) + ".00" if isinstance(input, int) else input)
