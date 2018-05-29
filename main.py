#!/usr/bin/env python3
import youtube_dl
import tempfile
import os
import sys
import re
import json
from pydub import AudioSegment
import argparse
import urllib
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
import tracklist

class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

# Megaman OST
# downloadAudio('https://www.youtube.com/watch?v=qzlUJk3-h_k')

# Simple class to hold individual song data and metadata
class Song(object):
    def __init__(self, data, song_name, album_name, track_num, coverfile=None):
        self.data = data
        self.title = song_name
        self.album = album_name
        self.track_num = track_num
        self.coverfile = coverfile

    def export(self, file_path, fileformat="mp3"):
        self.data.export(file_path, format=fileformat)
    
    def update_metadata(self, file_path):
        # Too lazy to read the spec, more efficient just to use ID3 to do
        # textual metadata and album art, but ¯\_(ツ)_/¯
        audio = EasyID3(file_path)
        audio['title'] = self.title
        audio['album'] = self.album
        audio['tracknumber'] = str(self.track_num)
        audio.save()

        if self.coverfile:
            audio = ID3(file_path)
            with open(self.coverfile, 'rb') as f:
                audio['APIC'] = APIC(
                        encoding=3, # 3 is for utf-8
                        mime='image/jpeg', # image/jpeg or image/png
                        type=3, # 3 is for the cover image
                        desc=u'Cover',
                        data=f.read()
                )
            audio.save()

# Simple class to hold info about the OST
class FullOst(object):
    def __init__(self, description_file, info_dict, audio_filename):
        self.description_file = description_file
        self.info = info_dict
        self.audio_file = audio_filename
        # If chapters was not populated, then we take matters into our own hands
        # 😤😤😤😤
        if not self.info['chapters']:
            chapters = {}
            with open(self.description_file) as f:
                chapters = tracklist.TrackList(f.read())
            self.info['chapters'] = chapters
        else:
            self.tracklist = tracklist.TrackList.from_chapters(chapters)

    # Youtube-dl removes the timestamp, but often the description will wrap the timestamp in
    # parens or square brackets.
    def __scrub_song_name(self, name):
        return name.replace('[]','').replace('()','').strip()

    def fetch_album_art(self, directory):
        urllib.request.urlretrieve(self.info['thumbnail'], "%s/art.jpeg" % (directory))

    # split single audio file into individual songs, saved at output_dir
    def splitOST(self, output_dir):
        album_folder = "%s/%s" %(output_dir, self.info['fulltitle'])
        try:
            os.mkdir(album_folder)
        except FileExistsError:
            if not os.path.isdir(album_folder):
                print("File %s already exists and is not a folder", album_folder)
                sys.exit(1)

        fullOSTAudio = AudioSegment.from_mp3(self.audio_file)

        self.fetch_album_art(album_folder)

        for i,track in enumerate(self.tracklist):
            # Seconds --> Milliseconds
            start_time = int(track.start) * 1000
            # Last track in the tracklist may not have an end timestamp
            if track.end:
                end_time =  int(track.end) * 1000
            else:
                end_time = len(fullOSTAudio)
            audio_segment = fullOSTAudio[start_time:end_time]
            song_name = self.__scrub_song_name(track.title)

            print("Song: " + song_name)
            print("Folder: " + album_folder)

            # Only supporting mp3 for now; downloading from YT so it ain't
            # exactly audiophile grade material we're working with here
            song_filename = "%s/%s.%s" % (album_folder, song_name, 'mp3')
            song = Song(audio_segment, song_name, self.info['fulltitle'], i, "%s/art.jpeg" % (album_folder))
            song.export(song_filename, "mp3")
            song.update_metadata(song_filename)

# Remove .m4a, .description, and .json files in tmp dir
def cleanUpTempDir():
    pass

def downloadAudio(url, download_dir=None):
    if download_dir == None:
        download_dir = os.getcwd()
    # ydl_opts = {
    #     'writedescription': True,
    #     'writeinfojson': True,
    #     'outtmpl': download_dir + '/' + 'AUDIO.%(ext)s',
    #     'logger': MyLogger(),
    #     'format': 'bestaudio[ext=m4a]'
    # }

    ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            'nopostoverwrites': True,
        }],
        'keepvideo': True,
        'writedescription': True,
        'writeinfojson': True,
        'outtmpl': download_dir + '/' + 'AUDIO.%(ext)s',
        'logger': MyLogger(),
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    parser = argparse.ArgumentParser(description='Download and split Full OST from Youtube link')
    parser.add_argument('url', type=str, help='youtube link to download from')
    parser.add_argument('--outputdir', type=str, default=os.getcwd(), required=False, help='directory to output songs to')
    parser.add_argument('--tmpdir', type=str, default=tempfile.mkdtemp(), required=False, help='staging directory for store full ost and metadata')
    args = parser.parse_args()
    tmpdir = os.path.abspath(args.tmpdir)
    outputdir = os.path.abspath(args.outputdir)

    downloadAudio(args.url, download_dir=args.tmpdir)
    description_file="%s/%s" % (args.tmpdir,'AUDIO.description')
    info_file="%s/%s" % (args.tmpdir,'AUDIO.info.json')

    info_dict = {}
    with open(info_file,"r") as f:
        data = f.read()
        info_dict = json.loads(data)

    audio_filename = info_dict['_filename'].replace(info_dict['ext'], 'mp3')
    ost = FullOst(description_file,info_dict, audio_filename)
    ost.splitOST(outputdir)

if __name__ == '__main__':
    main()