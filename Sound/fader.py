"""Simple faders."""
import pygame


# Maybe you can subclass the pygame.mixer.Sound and
# add the methods below to it..
class Fader(object):
    """Fader classes."""

    instances = []

    def __init__(self, fname):
        """Initialize fader."""
        super(Fader, self).__init__()
        self.sound = pygame.mixer.Sound(fname)
        # tweak for speed of effect!!
        self.increment = 0.1
        # fade to 100 on start
        self.next_vol = 1
        Fader.instances.append(self)

    def fade_to(self, new_vol):
        """Fade volume to new value."""
        self.next_vol = new_vol

    def set_volume(self, vol):
        """Set volume and next volume."""
        self.next_vol = vol
        self.sound.set_volume(vol)

    def play(self):
        """Play sound."""
        self.sound.play()

    @classmethod
    def update(cls):
        """Update static method."""
        for inst in cls.instances:
            curr_volume = inst.sound.get_volume()
            # print("{} : {} => {}".format(inst, curr_volume, inst.next_vol))
            if inst.next_vol > curr_volume:
                if curr_volume + inst.increment > 1:
                    inst.sound.set_volume(1)
                else:
                    inst.sound.set_volume(curr_volume + inst.increment)

            elif inst.next_vol < curr_volume:
                if curr_volume - inst.increment < 0:
                    inst.sound.set_volume(0)
                else:
                    inst.sound.set_volume(curr_volume - inst.increment)


if __name__ == '__main__':
    # pylint: disable= E1101
    # pygame.init()
    pygame.mixer.init()
    SOUND1 = Fader("Music/Storm.ogg")
    SOUND2 = Fader("Music/Rise.ogg")
    SOUND1.sound.play()
    SOUND2.sound.play()
    SOUND2.sound.set_volume(0)

    # fading..
    SOUND1.fade_to(0)
    SOUND2.fade_to(1)

    while True:
        Fader.update()
