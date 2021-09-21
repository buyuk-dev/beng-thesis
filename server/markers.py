""" 2021 Created by michal@buyuk-dev.com
"""

from pylsl import StreamInfo, StreamInlet, StreamOutlet, resolve_stream, local_clock


class MarkerStream:
    def __init__(self, choices):
        self.markers = choices
        self.info = StreamInfo("Markers", "Markers", 1, 0, "string", "UniqueId0723")
        self.outlet = StreamOutlet(self.info)

    def push(self, marker):
        if not marker in self.markers:
            raise ValueError(f"Marker {marker} unknown.")
        self.outlet.push_sample([marker], local_clock())


class MarkerReader:
    def __init__(self):
        streams = resolve_stream("type", "Markers")
        self.inlet = StreamInlet(streams[0])

    def pull_sample(self):
        sample, timestamp = self.inlet.pull_sample()
        return sample, timestamp


def main():
    MARKERS = ["like", "dislike", "meh", "start", "stop"]
    stream = MarkerStream(MARKERS)
    while True:
        marker = input("Marker >> ")
        try:
            stream.push(marker)
        except ValueError as e:
            print(e)


if __name__ == "__main__":
    main()
