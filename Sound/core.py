"""Core sound script."""
import sys
import time
import multiprocessing
from Sound.micro import Micro
from pygame import mixer
import alsaaudio
import audioop
import numpy as np


# pylint: disable=E1101
class Sound(multiprocessing.Process):
    """Sound process."""

    def __init__(self, time_seconds, file_music, shared_value, video_exit):
        """Initialize class."""
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.time_seconds = time_seconds
        self.file_music = file_music
        self.shared_value = shared_value
        self.video_exit = video_exit

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
            df = np.zeros(n_intervals)

            # create an other process to real time display
            # t1 = MyProcess(df, 1 / interval, time_seconds)
            # t1.start()

            # init the last mean
            # and the music
            last_mean = 1
            mixer.init()
            mixer.music.load(self.file_music)
            mixer.music.set_volume(0.6)
            mixer.music.play()

            while i < n_intervals:
                # Read data from device
                l, data = inp.read()
                if l:
                    # Return the maximumof the absolute value of all samples
                    # in a fragment.
                    df[i] = audioop.max(data, 2)
                i += 1
                time.sleep(interval)

                # update the music every half of second
                if i % 500 == 0:

                    # change data to decibel
                    a = 20 * np.log10(df)
                    a[np.isinf(a)] = 0
                    # try to do the mean
                    try:
                        mean = np.mean(a[a > 0][-500:])
                    except IndexError:
                        mean = 1

                    # compute the ratio
                    ratio = mean / last_mean
                    # to avoid the first ratio which is mean/1
                    if last_mean == 1:
                        ratio = 1
                    last_mean = mean
                    # set the new volume
                    mixer.music.set_volume(
                        mixer.music.get_volume() * (1 + 10 * (1 - ratio))
                        )
                    print("ratio = ", (1 + 10 * (1 - ratio)))
            self.video_exit.set()
            mixer.music.stop()
            mixer.quit()
            self.exit.set()


if __name__ == '__main__':
    SHARED_VALUE = multiprocessing.Value('d', 0.0)
    if len(sys.argv) > 1:
        SOUND = Sound(int(sys.argv[2]), sys.argv[1], SHARED_VALUE, None)
    else:
        SOUND = Sound(60, "./music.mp3", SHARED_VALUE, None)
    SOUND.run()
