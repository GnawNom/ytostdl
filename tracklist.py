import re
import collections
# Hour:Min:Sec
timestamp_pattern = r'(([0-9]?[0-9]:)?[0-5]?[0-9]:[0-5][0-9])'
#same pattern as above but wrapped in ([])
timestamp_pattern_wrapped = r'[\(|\[]?' + timestamp_pattern + r'[\)|\]]?'
#TODO define the start+end timestamp pattern
start_end_timestamp_pattern =  timestamp_pattern_wrapped + r'.*' + timestamp_pattern_wrapped
timestamp_reg = re.compile(timestamp_pattern_wrapped)
start_end_timestamp_reg = re.compile(start_end_timestamp_pattern)

SingleTimestampSongLine = collections.namedtuple("SingleTimestampSongLine", 'timestamp songname')
DoubleTimestampSongLine = collections.namedtuple("DoubleTimestampSongLine", 'start_timestamp end_timestamp songname')

class Timestamp(object):
    def __init__(self, ts):
        self.timestamp = ts

    def to_seconds(self):
        """ Return the timestamp in terms of total seconds
        >>> ts=Timestamp('01:45:59') 
        >>> ts.to_seconds()
        6359
        """
        parts = self.timestamp.split(":")
        total_seconds = 0
        for i in range(len(parts)):
            seconds = 60**(i)
            total_seconds += int(parts[len(parts)-1-i]) * seconds
        return total_seconds

    def __string__(self):
        return self.timestamp
    
    def __repr__(self):
        'tracklist.timestamp(%s)' % self.timestamp

class Track(object):
    def __init__(self, start, end, title):
        self.start = start
        self.end = end
        self.title = title

def __init__(self, description):
    self.description=description
    self.build_tracklist()
    self.tracks = []


class TrackList(object):
    def __init__(self, description):
        self.description = description
        self.build_tracklist()

    @classmethod
    # TODO create a tracklist using chapters
    def from_chapters(self, chapters):
        pass
    
    def build_tracklist(self):
        tuples = []
        tracks = []
        # TODO, kinda ugly, cleanup later?
        for i,l in enumerate(self.description.splitlines()):
            matched = timestamp_reg.search(l)
            if matched:
                #Split the string, and extact matching timestamps 
                timestamp_matches = tuple(map(lambda x: timestamp_reg.match(x).group(0), filter(lambda x: x and timestamp_reg.match(x), timestamp_reg.split(l))))
                if len(timestamp_matches) == 1:
                    timestamp = Timestamp(timestamp_matches[0])
                    wrapped_timestamp = matched.group()
                    # Remove the timestamp from the line
                    songName = l.replace(wrapped_timestamp, "").strip()
                    tuples.append(SingleTimestampSongLine(timestamp, songName))
                else:
                    start_timestamp = Timestamp(timestamp_matches[0])
                    end_timestamp = Timestamp(timestamp_matches[1])
                    timestamps_string = start_end_timestamp_reg.search(l).group()
                    songName = l.replace(timestamps_string, "").strip()
                    tracks.append(Track(start_timestamp, end_timestamp, songName))

        # Should only be necessary if the descriptions have single timestamps
        for i,t in enumerate(tuples):
            start_timestamp = Timestamp(t.timestamp)
            title = t.songname
            if i == len(tuples)-1:
                end_timestamp = None
            else:
                end_timestamp = Timestamp(tuples[i+1].timestamp)
            tracks.append(Track(start_timestamp, end_timestamp, title))
                
        self.tracks = tracks