"""MyProcess module."""
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pylab


# pylint: disable=E1101
class MyProcess(multiprocessing.Process):
    """MyprocessClass."""

    def __init__(self, array, seconde_size, total_loop):
        """
        Initialize the process.

        array -> a shared array between process
        seconde_size -> the numbers of sampling by unity of time
        total_loop -> the numbers of unity of time
        """
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.array = array
        self.seconde_size = seconde_size
        self.total_loop = total_loop

    def old_run(self):
        """Plot consideration."""
        sns.set_style('darkgrid')
        plt.ion()

        seconde_size = int(self.seconde_size)
        total_loop = int(self.total_loop)

        # we wait the stop signal from the main process
        while not self.exit.is_set():
            plt.clf()
            # decibel part
            array = 20 * np.log10(self.array)
            array[np.isinf(array)] = 0
            plt.plot(array, label="decibel volume")
            # mean parts
            # create the vector and fill it
            mean = np.zeros(len(array))
            for ele in range(total_loop):
                # get the interval
                res = array[ele * seconde_size: (ele + 1) * seconde_size]
                res = [np.mean(res[res > 0])] * seconde_size
                # assign it
                mean[ele * seconde_size: (ele + 1) * seconde_size] = res
            # plot the mean
            plt.plot(mean, label="mean every seconds", color="r")
            plt.grid(True)
            plt.legend()

            plt.draw()
            # refresh every 0.5 seconds
            pylab.waitforbuttonpress(timeout=0.5)
        print("Stopped")

    def shutdown(self):
        """Way to be notified when the process needs to stop."""
        self.exit.set()
