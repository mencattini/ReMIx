"""Main project entry point."""
import multiprocessing
import argparse
import yaml
from Sound.core import Sound
from Video.core import VideoEmotion


def __parsing__():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config", help="Configuration file.", default="./config/config.yml"
        )

    return parser.parse_args()


if __name__ == '__main__':
    ARGS = __parsing__()

    with open(ARGS.config) as config_file:
        CONFIG = yaml.load(config_file)
        SHARED_VALUE = multiprocessing.Value('i', 4)
        VIDEO = VideoEmotion(CONFIG['classifier'], SHARED_VALUE)
        SOUND = Sound(CONFIG['duration'], CONFIG['music'], SHARED_VALUE,
                      VIDEO.exit)
        VIDEO.start()
        SOUND.start()
