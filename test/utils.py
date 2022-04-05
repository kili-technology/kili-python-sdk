from datetime import datetime, timedelta
from functools import wraps


class burstthrottle(object):
    """
    Decorator that prevents a function from being called more that a certain amount of time
    To create a function that cannot be called more than 250 times in a minute:
        @burstthrottle(max_hits = 250, minutes = 1)
        def my_fun():
            pass
    """

    def __init__(self, max_hits, seconds=0, minutes=1, hours=0, error_message='TooManyCalls'):
        self.burst_window = timedelta(
            seconds=seconds, minutes=minutes, hours=hours)
        self.error_message = error_message
        self.hits = 0
        self.max_hits = max_hits
        self.timestamp = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            if now < self.timestamp + self.burst_window:
                if self.hits < self.max_hits:
                    self.hits += 1
                    return fn(*args, **kwargs)
                else:
                    self.timestamp = datetime.min
                    self.hits = 0
                    raise ValueError(self.error_message)

            else:
                self.timestamp = datetime.now()
                self.hits = 1
                return fn(*args, **kwargs)

        return wrapper
