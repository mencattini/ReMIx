"""Main project entry point."""
import multiprocessing
import argparse
from Sound.core import Sound
from Video.core import VideoEmotion


def __parsing__():
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

    return parser.parse_args()


if __name__ == '__main__':
    SHARED_VALUE = multiprocessing.Value('d', 4.0)
    ARGS = __parsing__()
    VIDEO = VideoEmotion(ARGS.training, SHARED_VALUE)
    SOUND = Sound(ARGS.time, ARGS.music, SHARED_VALUE, VIDEO.exit)
    VIDEO.start()
    SOUND.start()
