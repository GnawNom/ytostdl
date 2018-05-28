import youtube_dl
import tempfile
import pydub
import os
import re

class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


# tmpdir=tempfile.mkdtemp()
# print(tmpdir)
tmpdir=os.getcwd()
print(tmpdir)

def downloadAudio(url):
    ydl_opts = {
        'writedescription': True,
        'writeinfojson': True,
        'outtmpl': tmpdir + '/' + 'AUDIO.%(ext)s',
        'logger': MyLogger(),
        'format': 'bestaudio[ext=m4a]'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Megaman OST
# downloadAudio('https://www.youtube.com/watch?v=qzlUJk3-h_k')

# Overwatch OST
downloadAudio('https://www.youtube.com/watch?v=DytVLscuUdI')

# Hour:Min:Sec
timestamp_pattern = r'(?:([0-9]?[0-9]):)?([0-5]?[0-9]):([0-5][0-9])'
#same pattern as above but wrapped in ([])
timestamp_pattern_wrapped = r'[\(|\[]?' + timestamp_pattern + r'[\)|\]]?'
timestamp_reg = re.compile(timestamp_pattern)
timestamp_wrapped_reg = re.compile(timestamp_pattern_wrapped)

# Parse description and get a list of (timestamp, song name) tuples
def get_timestamps(filename):
    tuples = []
    with open(tmpdir+'/'+'AUDIO.description') as f:
        lines = f.read().splitlines()
        for l in lines:
            matched = timestamp_reg.search(l)
            if matched:
                timestamp = matched.group()
                wrapped_timestamp = timestamp_wrapped_reg.search(l).group()
                # Remove the timestamp from the line
                songName = l.replace(wrapped_timestamp, "").strip()
                tuples.append((timestamp, songName))
    return tuples

# Simple class to hold info about the OST
class FullOst(object):
    def __init__(self, description_file, audio_file, info_json_file):
        self.audio_file = audio_file
        self.description_file = description_file
        self.info_json_file = info_json_file
        self.timestamps_and_songs = self.__parse_timestamps_and_songs()

    def __parse_timestamps_and_songs(self):
        return get_timestamps(self.description_file)

    # split single audio file into individual songs, saved at output_dir
    def splitOST(self, output_dir):
        pass

# Remove .m4a, .description, and .json files in tmp dir
def cleanUpTempDir():
    pass