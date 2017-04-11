#! /usr/bin/python3

import alsaaudio
import time
import audioop
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage.filters import gaussian_laplace
import pylab
import multiprocessing


class MyProcess(multiprocessing.Process):
    def __init__(self, array, seconde_size, total_loop):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.array = array
        self.seconde_size = seconde_size
        self.total_loop = total_loop

    def run(self):
        sns.set_style('darkgrid')
        plt.ion()

        seconde_size = int(self.seconde_size)
        total_loop = int(self.total_loop)

        while not(self.exit.is_set()):

                plt.clf()
                # decibel part
                a = 20 * np.log10(self.array)
                a[np.isinf(a)] = 0
                plt.plot(a, label="decibel volume")
                # mean parts
                # create th vector and fill it
                mean = np.zeros(len(a))
                for ele in range(total_loop):
                    # get the interval
                    res = a[ele * seconde_size: (ele + 1) * seconde_size]
                    res = [np.mean(res[res > 0])] * seconde_size
                    # assign it
                    mean[ele * seconde_size: (ele + 1) * seconde_size] = res
                plt.plot(mean, label="mean every seconds", color="r")
                plt.grid(True)
                plt.legend()

                plt.draw()
                pylab.waitforbuttonpress(timeout=0.1)
        print("Stopped")

    def shutdown(self):
        self.exit.set()


class Micro():

    def __init__(self, alsaaudio_capture, alsaaudio_nonblock):
        self.capture = alsaaudio_capture
        self.nonblock = alsaaudio_nonblock

    def __enter__(self):
        self.inp = alsaaudio.PCM(self.capture, self.nonblock)
        return self.inp

    def __exit__(self, capture, nonblock, inpt):
        self.inp.close()


def main(time_seconds, to_file):
    """
    Where time is the numbers of seconds!!!!
    """

    # Open the device in nonblocking capture mode. The last argument could
    # just as well have been zero for blocking mode. Then we could have
    # left out the sleep call in the bottom of the loop
    with Micro(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK) as inp:

        # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
        inp.setchannels(1)
        inp.setrate(8000)
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

        # The period size controls the internal number of frames per period.
        # The significance of this parameter is documented in the ALSA api.
        # For our purposes, it is suficcient to know that reads from the device
        # will return this many frames. Each frame being 2 bytes long.
        # This means that the reads below will return either 320 bytes of data
        # or 0 bytes of data. The latter is possible because we are in nonblocking
        # mode.
        inp.setperiodsize(160)

        i = 0
        interval = 0.001
        n = int(time_seconds / interval)
        df = multiprocessing.Array('i', n)

        t1 = MyProcess(df, 1 / interval, time_seconds)
        t1.start()

        while i < n:
            # Read data from device
            l, data = inp.read()
            if l:
                # Return the maximumof the absolute value of all samples in a fragment.
                df[i] = audioop.max(data, 2)
            i += 1
            time.sleep(interval)
            # print(i, "s")

        if to_file:
            df[400:].tofile("out.dat", sep=',')

        input("Waiting input")
        t1.shutdown()
    return np.array(df[400:])


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
    df = main(10, False)
    # plotting(df)
