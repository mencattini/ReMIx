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
    shared_value = multiprocessing.Value('d', 4.0)
    args = __parsing__()
    video = VideoEmotion(args.training, shared_value)
    sound = Sound(args.time, args.music, shared_value, video.exit)
    video.start()
    sound.start()
