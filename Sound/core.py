#! /usr/bin/python3

from Sound.micro import Micro
from pygame import mixer
import alsaaudio
import time
import audioop
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage.filters import gaussian_laplace
import sys
import multiprocessing


class Sound(multiprocessing.Process):

    def __init__(self, time_seconds, to_file, file_music, shared_value):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.time_seconds = time_seconds
        self.to_file = to_file
        self.file_music = file_music
        self.shared_value = shared_value

    def run(self):
        """
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
            n = int(self.time_seconds / interval)
            # a memory shared vector
            # df = multiprocessing.Array('i', n)
            df = np.zeros(n)

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

            while i < n:
                # Read data from device
                l, data = inp.read()
                if l:
                    # Return the maximumof the absolute value of all samples
                    # in a fragment.
                    df[i] = audioop.max(data, 2)
                i += 1
                time.sleep(interval)

                # update the music every half of second
                if (i % 500 == 0):

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

            mixer.music.stop()
            mixer.quit()

            if self.to_file:
                df[400:].tofile("out.dat", sep=',')

            # stop the other process
            # t1.shutdown()
        return np.array(df[400:])

        def shutdown(self):
            # way to be notified when the process needs to stop
            self.exit.set()


def plotting(df):

    sns.set_style('darkgrid')
    plt.subplot(2, 2, 1)
    plt.plot(df, label="raw data")
    plt.grid(True)
    plt.legend()

    a = 20 * np.log10(df)
    a[np.isinf(a)] = 0
    plt.subplot(2, 2, 2)
    plt.plot(a, label="decibel volume")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(np.fft.fft(a), label="fft(raw data)")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(gaussian_laplace(a, sigma=max(a)), label="gaussian(raw data)")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == '__main__':

    shared_value = multiprocessing.Value('d', 0.0)
    if len(sys.argv) > 1:
        sound = Sound(int(sys.argv[2], False, sys.argv[1]), shared_value)
    else:
        sound = Sound(60, False, "./music.mp3", shared_value)
    sound.run()
