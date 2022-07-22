import traceback
from datetime import datetime, timedelta
from functools import wraps

COUNT_SAMPLE_MAX = 26000


class burstthrottle(object):
    """
    Decorator that prevents a function from being called more that a certain amount of time
    To create a function that cannot be called more than 250 times in a minute:
        @burstthrottle(max_hits = 250, minutes = 1)
        def my_fun():
            pass
    """

    def __init__(self, max_hits, seconds=0, minutes=1, hours=0, error_message="TooManyCalls"):
        self.burst_window = timedelta(seconds=seconds, minutes=minutes, hours=hours)
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


@burstthrottle(max_hits=250, minutes=1)
def mocked_query_method(skip, first, *_):
    """
    Simulates a query result by returning a list of ids
    """
    max_range = min(COUNT_SAMPLE_MAX, skip + first)
    res = [{"id": i} for i in range(skip, max_range)]
    return res


@burstthrottle(max_hits=250, minutes=1)
def mocked_count_method(*_):
    """
    Simulates a count query
    """
    return COUNT_SAMPLE_MAX


def debug_subprocess_pytest(result):
    print(result.output)
    if result.exception is not None:
        traceback.print_tb(result.exception.__traceback__)
        print(result.exception)
    assert result.exit_code == 0
