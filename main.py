from Sound.core import Sound
from Video.core import VideoStream
import multiprocessing
import argparse


def parsing():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--music", help="The file path of music", default="./Sound/music.mp3"
        )
    parser.add_argument(
        "--time", help="Numbers of seconds", type=int, default=60
        )
    parser.add_argument(
        "--training",
        help="The file path of training",
        default="./Video/classifier.pkl"
        )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    shared_value = multiprocessing.Value('d', 4.0)
    args = parsing()
