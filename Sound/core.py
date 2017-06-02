"""Core sound script."""
import sys
import time
import multiprocessing
from collections import Counter

from pygame import mixer
import alsaaudio
import audioop
import numpy as np
from Sound.micro import Micro
from Sound.fader import Fader
from Video.constants import EMOTIONS


MIN_COUNTER = 15


# pylint: disable=E1101, R0913, R0914, R0915, C0200, R0912, R0902
class Sound(multiprocessing.Process):
    """Sound process."""

    def __init__(self, time_seconds, file_music, shared_value, flag,
                 video_exit, demo=False):
        """Initialize class."""
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.time_seconds = time_seconds
        self.file_music = file_music
        self.sounds = []
        self.shared = shared_value
        self.flag = flag
        self.video_exit = video_exit
        self.demo = demo

    def run(self):
        """Execute the process.

        Where time is the numbers of seconds!!!!
        """
        with Micro() as inp:

            # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
            inp.setchannels(1)
            inp.setrate(8000)
            inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

            # The period size controls the internal number of frames per
            # period. The significance of this parameter is documented in the
            # ALSA api.For our purposes, it is suficcient to know that reads
            # from the device will return this many frames. Each frame being 2
            # bytes long. This means that the reads below will return either
            # 320 bytes of data or 0 bytes of data. The latter is possible
            # because we are in nonblocking mode.
            inp.setperiodsize(160)

            # i is the number of loop
            i = 0
            # the numbers of sampling for each unity of time
            interval = 0.001
            # the total of sampling
            n_intervals = int(self.time_seconds / interval)
            # a memory shared vector
            # df = multiprocessing.Array('i', n)
            deltaf = np.zeros(n_intervals)

            # create an other process to real time display
            # t1 = MyProcess(df, 1 / interval, time_seconds)
            # t1.start()

            # init the last mean
            # and the music
            last_mean = 1
            mixer.init()
            for i in range(len(EMOTIONS)):
                self.sounds.append(Fader(self.file_music[EMOTIONS[i]]))
                self.sounds[-1].set_volume(0)
                self.sounds[-1].play()

            volume = 1.0
            self.sounds[4].set_volume(1)

            print('play')
            current_value = 4
            emotion = []
            counter = 0
            while i < n_intervals:
                # Read data from device
                flag, data = inp.read()
                if flag:
                    # Return the maximumof the absolute value of all samples
                    # in a fragment.
                    deltaf[i] = audioop.max(data, 2)
                i += 1
                time.sleep(interval)
                if self.flag.value:
                    print("Emotion: {}".format(EMOTIONS[self.shared.value]))
                    self.flag.value = False
                    counter += 1
                    emotion.append(self.shared.value)
                    if counter == MIN_COUNTER:
                        counter = Counter(emotion)
                        new_emotion = counter.most_common()[0][0]
                        emotion = []
                        counter = 0
                        print("\033[0;32mAvarage emotion: {}\033[0m".format(
                            EMOTIONS[new_emotion]))
                        if new_emotion != current_value:
                            print("Change music: {} -> {}".format(
                                EMOTIONS[current_value],
                                EMOTIONS[new_emotion]))
                            self.sounds[current_value].fade_to(0)
                            old_value = self.shared.value
                            current_value = old_value
                            self.sounds[current_value].fade_to(volume)
                            counter = 0

                # update the music every half of second
                if i % 500 == 0:

                    # change data to decibel
                    array = 20 * np.log10(deltaf)
                    array[np.isinf(array)] = 0
                    # try to do the mean
                    try:
                        mean = np.mean(array[array > 0][-500:])
                    except IndexError:
                        mean = 1
                    if self.demo:
                        if np.random.random() < 0.5:
                            ratio = 1 + np.abs(np.random.normal(0, 0.01))
                        else:
                            ratio = 1 - np.abs(np.random.normal(0, 0.01))
                    else:
                        # compute the ratio
                        ratio = mean / last_mean
                        # to avoid the first ratio which is mean/1
                        if last_mean == 1:
                            ratio = 1
                    last_mean = mean
                    # set the new volume
                    volume *= (1 + 10 * (1 - ratio))
                    self.sounds[current_value].set_volume(volume)
                    Fader.update()
                    print("ratio = ", (1 + 10 * (1 - ratio)))
            self.video_exit.set()
            mixer.music.stop()
            mixer.quit()
            self.exit.set()


if __name__ == '__main__':
    SHARED_VALUE = multiprocessing.Value('d', 0.0)
    FLAG_VALUE = multiprocessing.Value('b', False)
    if len(sys.argv) > 1:
        SOUND = Sound(int(sys.argv[2]), sys.argv[1], SHARED_VALUE,
                      FLAG_VALUE, None)
    else:
        SOUND = Sound(60, "./music.mp3", SHARED_VALUE, FLAG_VALUE, None)
    SOUND.run()
