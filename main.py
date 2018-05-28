import youtube_dl
import tempfile
import os
import re
import json
from pydub import AudioSegment
import argparse

class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)



# Megaman OST
# downloadAudio('https://www.youtube.com/watch?v=qzlUJk3-h_k')

# Overwatch OST
downloadAudio('https://www.youtube.com/watch?v=DytVLscuUdI')

# Simple class to hold info about the OST
class FullOst(object):
    def __init__(self, description_file, info_json_file):
        self.description_file = description_file
        self.info = json.loads(info_json_file)
        self.audio_file = self.info['_filename']
        self.timestamps_and_songs = self.__parse_timestamps_and_songs()

    # Youtube-dl removes the timestamp, but often the description will wrap the timestamp in
    # parens or square brackets.
    def __scrub_song_name(self, song):
        return song.replace('[]','').replace('()','')

    def __parse_timestamps_and_songs(self):
        return get_timestamps(self.description_file)

    # split single audio file into individual songs, saved at output_dir
    def splitOST(self, output_dir):
        chapters = self.info['chapters']
        extension = self.info['extension']
        fullsong = AudioSegment.from_file(self.audio_file, extension)
        for chapter in chapters:
            start_time = int(chapter['start_time']) * 1000
            end_time =  int(chapter['end_time']) * 1000
            song = fullsong[start_time:end_time]
            song_name = self.__scrub_song_name(chapter['tile'])
            song.export(os.path.abspath(output_dir + '/' + song_name), format="mp3")


# Remove .m4a, .description, and .json files in tmp dir
def cleanUpTempDir():
    pass

def downloadAudio(url, download_dir=None):
    if download_dir == None:
        download_dir = os.getcwd()
    ydl_opts = {
        'writedescription': True,
        'writeinfojson': True,
        'outtmpl': download_dir + '/' + 'AUDIO.%(ext)s',
        'logger': MyLogger(),
        'format': 'bestaudio[ext=m4a]'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    parser = argparse.ArgumentParser(description='Download and split Full OST from Youtube link')
    parser.add_argument('url', type=str, help='youtube link to download from', required=True)
    parser.add_argument('--outputdir', type=str, default=os.getcwd(), help='directory to output songs to', required=False)
    args = parser.parse_args()

    tmpdir=tempfile.mkdtemp()
    downloadAudio(args.url, download_dir=tmpdir)
    description_file="%s/%s" % (tmpdir,'AUDIO.description')
    info_file="%s/%s" % (tmpdir,'AUDIO.info.json')
    ost = FullOst(description_file,info_file)
    ost.splitOST(args.outputdir)

if __name__ == '__main__':
    main()