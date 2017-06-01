"""Main project entry point."""
import multiprocessing
import argparse
<<<<<<< HEAD
import yaml
=======
>>>>>>> 529c52b9e1040432c464eb41cea1456554edb373
from Sound.core import Sound
from Video.core import VideoEmotion


def __parsing__():
    parser = argparse.ArgumentParser()

    parser.add_argument(
<<<<<<< HEAD
        "--config", help="Configuration file.", default="./config/config.yml"
=======
        "--music", help="The file path of music", default="./Sound/music.mp3"
        )
    parser.add_argument(
        "--time", help="Numbers of seconds", type=int, default=60
        )
    parser.add_argument(
        "--training",
        help="The file path of training",
        default="./Video/classifier.pkl"
>>>>>>> 529c52b9e1040432c464eb41cea1456554edb373
        )

    return parser.parse_args()


if __name__ == '__main__':
<<<<<<< HEAD
    ARGS = __parsing__()

    with open(ARGS.config) as config_file:
        CONFIG = yaml.load(config_file)
        SHARED_VALUE = multiprocessing.Value('i', 4)
        FLAG_VALUE = multiprocessing.Value('b', False)
        VIDEO = VideoEmotion(CONFIG['classifier'], SHARED_VALUE, FLAG_VALUE)
        SOUND = Sound(CONFIG['duration'], CONFIG['music'], SHARED_VALUE,
                      FLAG_VALUE, VIDEO.exit)
        VIDEO.start()
        SOUND.start()
=======
    shared_value = multiprocessing.Value('d', 4.0)
    args = __parsing__()
    video = VideoEmotion(args.training, shared_value)
    sound = Sound(args.time, args.music, shared_value, video.exit)
    video.start()
    sound.start()
>>>>>>> 529c52b9e1040432c464eb41cea1456554edb373
