#! /usr/bin/python3

from micro import Micro
from myprocess import MyProcess

import alsaaudio
import time
import audioop
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage.filters import gaussian_laplace
import multiprocessing


def main(time_seconds, to_file):
    """
    Where time is the numbers of seconds!!!!
    """

    with Micro() as inp:

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

        # i is the number of loop
        i = 0
        # the numbers of sampling for each unity of time
        interval = 0.001
        # the total of sampling
        n = int(time_seconds / interval)
        # a memory shared vector
        df = multiprocessing.Array('i', n)
        # create an other process to real time display
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

        if to_file:
            df[400:].tofile("out.dat", sep=',')

        input("Waiting input")
        # stop the other process
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
