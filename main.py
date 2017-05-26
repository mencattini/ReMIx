from Sound.core import Sound
from Video.core import VideoStream
import multiprocessing


if __name__ == '__main__':
    shared_value = multiprocessing.Value('d', 4.0)
