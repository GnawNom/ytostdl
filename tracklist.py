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

class TrackList(object):
    class Track(object):
        def __init__(self, start, end, title):
            self.start = start
            self.end = end
            self.title = title

    def __init__(self, description):
        self.description=description
        self.build_tracklist()
        self.tracks = []

    @classmethod
    # TODO create a tracklist using chapters
    def from_chapters(self, chapters):
        pass
    
    def build_tracklist(self):
        tuples = []
        tracks = []
        # TODO, kinda ugly, cleanup later?
        for i,l in enumerate(self.description.splitlines()):
            matched = start_end_timestamp_reg.search(l)
            if matched:
                start_timestamp = matched.group(1)
                end_timestamp = matched.group(4)
                timestamp = timestamp_reg.search(l).group()
                songName = l.replace(timestamp, "").strip()
                tracks.append(Track(start_timestamp, end_timestamp, songName))

            matched = timestamp_reg.search(l)
            if matched:
                timestamp = matched.group(2)
                wrapped_timestamp = matched.group()
                # Remove the timestamp from the line
                songName = l.replace(wrapped_timestamp, "").strip()
                tuples.append(SingleTimestampSongLine(timestamp, songName))

        # Should only be necessary if the descriptions have single timestamps
        for i,t in enumerate(tuples):
            start_timestamp = t.timestamp
            title = t.songname
            if i == len(tuples)-1:
                end_timestamp = None
            else:
                end_timestamp = tuples[i+1].timestamp
            tracks.append(Track(start_timestamp, end_timestamp))
                
        self.tracks = tracks