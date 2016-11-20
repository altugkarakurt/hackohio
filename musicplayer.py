from flask import url_for, Flask, render_template, redirect
import os
import fnmatch
import eyed3
import json
import functools

app = Flask(__name__)
eyed3.log.setLevel("ERROR")
db = "library.json"

def load_library():
    if(os.path.isfile(db)):
        return json.load(open(db, "r"))
    else:
        return []

def dump_library(jsondata):
    json.dump(jsondata, open(db, "w"))

def populate_library(dir_name="./static/music/", ext="*.mp3"):
    metadata = load_library()
    paths = [entry["path"] for entry in metadata]

    cnt = len(metadata)

    for idx, path in enumerate(paths):
        if(os.path.isfile(path)):
            del paths[idx]
            del metadata[idx]

    # check if the folder exists
    if(not os.path.isdir(dir_name)):
        return []

    # walk all the subdirectories
    for (path, _, files) in os.walk(dir_name):
        for f in files:
            if(fnmatch.fnmatch(f.lower(), ext.lower())):
                track_path = os.path.join(path, f)
                if(track_path not in paths):
                    track = eyed3.load(track_path)
                    paths.append(track_path)
                    cnt += 1
                    metadata.append({"title":track.tag.title, 
                                    "artist":track.tag.artist,
                                    "album":track.tag.album,
                                    "track_num":track.tag.track_num[0],
                                    "path":track_path,
                                    "tags":[],
                                    "id":cnt})
    dump_library(metadata)

@app.route("/")
def all_tracks():
    return render_template("music.html", tracks=load_library(), taglist=get_taglist())

def get_taglist():
    return set([tag for track in load_library() for tag in track["tags"]])

@app.route("/tagged/<tag>")
def tag_playlist(tag):
    tracklist = [entry for entry in load_library() if(tag in entry["tags"])]
    return render_template("music.html", tracks=tracklist, taglist=get_taglist())

app.debug = True
app.run()