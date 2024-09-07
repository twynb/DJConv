# DJUCED Database Format

The database format for DJUCED files isn't officially documented by Hercules, these are the results of reverse engineering it in the process of building DJConv. The database was reversed engineered for DJUCED version 5.3.7.

Contents:

- [playlists2](#playlists2)
- [recordings](#recordings)
- [samples](#samples)
- [sqliteSequence](#sqlitesequence)
- [tblAdmin](#tbladmin)
- [tblFolderScan](#tblfolderscan)
- [trackBeats](#trackbeats)
- [trackCues](#trackcues)
- [tracks](#tracks)
- [appendix](#appendix)
  - [color codes](#color-codes)
  - [song keys](#song-keys)

## playlists2

Playlist data. Contains both an entry for each playlist and an entry for each playlist entry.

| column | description | note |
| ------ | ----------- | ---- |
| name | name of the playlist | also used to associate playlists and entries |
| path | path for playlist | folder path playlist is in. # for playlists in the top path, #/folder/folder2 for playlists in folder/folder2. song entries match playlist's folder. |
| data | full file path to the song | empty for playlist entries |
| order_in_list | sort order | sort order of playlists in playlist view, or entries in playlist. |
| type | number denoting the type | 0 for playlist, 3 for playlist entries. 5 for DJUCED parties. |

## recordings

Sets recorded through DJUCED.

| column | description | note |
| ------ | ----------- | ---- |
| recordId | full file path | |

## samples

Samples to play from the sampler?

| column | description | note |
| ------ | ----------- | ---- |
| sampleId | full file path | |

## sqliteSequence

Reserved

## tblAdmin

Reserved, only contains one entry in test data ('DB_VERSION', 'GENERAL', 0.059)

| column | description | note |
| ------ | ----------- | ---- |
| key | data key | |
| group | data entry group | |
| keyval | value | |

## tblFolderScan

Empty in test data.

| column | description | note |
| ------ | ----------- | ---- |
| Scan | ? | |
| FolderID | ? | |
| FolderPath | ? | |
| DisplayName | ? | |

## trackBeats

Position of a track's beats.

| column | description | note |
| ------ | ----------- | ---- |
| trackId | full file path | used to link this to the track. |
| beatpos | first beat's offset | unit: seconds |
| timesignature | ??? | setting this to arbitrary values as a test didn't seem to have any effect |

## trackCues

Cue points.

| column | description | note |
| ------ | ----------- | ---- |
| trackId | full file path | used to link this to the track. |
| cuename | name of the cue point | defaults to "Cue $NUMBER", custom defined by user |
| cuenumber | number of the cue point | cuenumber 0 corresponts to pressing the "CUE" button. 1-8 correspond to hot cues. There are cue numbers from 1000 upwards, their prupose is unknown. |
| cuepos | position of the cue point | unit: seconds after song start |
| cueColor | color of the cue point | colors are hardcoded, see table in appendix |

## tracks

Track data.

| column | description | note |
| ------ | ----------- | ---- |
| album | song album | |
| albumartist | song album artist | |
| artist | song artist | |
| bitrate | the file's bitrate | |
| comment | comment | |
| composer | song composer | |
| coverimage | ? | presumably file path to cover image. |
| title | song title | |
| smart_advisor | ? | always null in test data.
| bpm | song bpm | |
| max_val_gain | ? | |
| tracknumber | track number | |
| drive | drive song is stored on | example: "D:/" |
| filepath | path to song directory | example: "D:/path/to/directory" |
| filename | file name | example: "song.mp3" |
| absolutepath | absolute path | example: "D:/path/to/directory/song.mp3" |
| filetype | file type | example: "mp3" |
| key | song key | keys are hardcoded, see appendix |
| genre | song genre | genre name as plain text, example: "Metal" |
| filesize | file size in bytes | |
| length | song length in seconds | |
| rating | ? | always 0 in test data. |
| filedate | last modified timestamp for file. | |
| year | song year | |
| playcount | how often song was played | |
| first_played | timestamp of first time song was played in DJUCED | |
| last_played | timestamp of last time song was played in DJUCED | |
| first_seen | timestamp of first time DJUCED detected song | |
| tags_read | ? | always 1 in test data. |
| waveform | blob data | presumably represents visible waveform. Setting it to null doesn't break DJUCED. |
| danceability | ? | number presumably indicating some danceability score calculated by DJUCED. |
| samplerate | song sample rate | unit: Hz |
| stores | ? | always null in test data. |

## Appendix

Additional information.

### Color Codes

Colors for cue points are hardcoded. The following values exist:

| value | color |
| ---- | ----- |
| 0 | dark blue |
| 1 | light blue |
| 2 | dark green |
| 3 | light green |
| 4 | red |
| 5 | pink |
| 6 | white |
| 7 | orange |
| 8 | yellow |

### Song Keys

Song keys are stored as a number between 0 and 23.
0-11 represent major keys (from 0 for A major to 11 for G# major),
12-23 represent minor keys (from 12 for A minor to 23 for G# minor).
