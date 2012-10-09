import sys

class ProgressIndicator(object):
    """
    A reusable progress indicator.
    """
    def __init__(self, *args, **kwargs):
        self.message = "\n".join(args)

    def flush(self):
        """
        Flushes standard output.
        """
        sys.stdout.write('\n')
        sys.stdout.write('\n')
        sys.stdout.flush()
        return True

    def clear_line(self):
        """
        Clears the line.
        """
        sys.stdout.write('\x1b[K')

    def move_up(self, distance=1):
        """
        Moves cursor up.
        """
        sys.stdout.write('\x1b[%dA' % distance)

    def move_down(self, distance=1):
        """
        Moves cursor down.
        """
        sys.stdout.write('\x1b[%dB' % distance)

    def move_left(self, distance=1):
        """
        Moves cursor to the left.
        """
        sys.stdout.write('\x1b[%dD' % distance)

    def write(self, *args):
        """
        Writes the indicator to the screen.
        """
        message = self.message % args
        self.clear_line()
        sys.stdout.write(message)
        self.move_left(len(message))
        self.move_down()
        sys.stdout.flush()


class SnakeIndicator(ProgressIndicator):
    """
    A "snake" progress indicator.
    """
    def __init__(self, *args, **kwargs):
        self.index = 1
        self.chrs = "_,.-*``*-.,_"
        self.length = len(self.chrs)
        super(SnakeIndicator, self).__init__(*args, **kwargs)

    def animate(self):
        """
        Animates the snake.
        """
        mod = self.index % self.length
        prefix = self.chrs[mod:]
        suffix = self.chrs[:mod]
        self.clear_line()
        sys.stdout.write(prefix + suffix)
        self.move_left(self.length)

        self.index += 1

        self.move_up(self.message.count('\n') + 1)
        sys.stdout.flush()


