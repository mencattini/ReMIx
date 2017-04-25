import alsaaudio


class Micro():
    """ Class to use micro in a `with` bloc """

    def __init__(self, alsaaudio_capture=alsaaudio.PCM_CAPTURE, alsaaudio_nonblock=alsaaudio.PCM_NONBLOCK):
        """
        Open the device in nonblocking capture mode. The last argument could
        just as well have been zero for blocking mode. Then we could have
        left out the sleep call in the bottom of the loop
        """
        self.capture = alsaaudio_capture
        self.nonblock = alsaaudio_nonblock

    def __enter__(self):
        """
        During the __enter__ function we set the acquisition and return it
        """
        self.inp = alsaaudio.PCM(self.capture, self.nonblock)
        return self.inp

    def __exit__(self, capture, nonblock, inpt):
        """
        During the exit, we just have to close the acquisition
        """
        self.inp.close()
