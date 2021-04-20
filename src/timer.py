import threading
from typing import Callable
from typing import Any
import datetime


class Timer:
    def __init__(self, t):
        self.t = t

    @property
    def time(self):
        return self.t

    @time.setter
    def time(self, t):
        self.t = t

    @time.deleter
    def time(self):
        del self.t

    def _get_diff(self) -> float:
        print("DEBUG time", self.t)
        now = datetime.datetime.now()
        h,m = self.t.split(":")[0], self.t.split(":")[1]
        nxt = datetime.datetime(now.year, now.month,
                now.day, int(h), int(m), 0)

        if nxt < now:
            nxt = nxt + datetime.timedelta(hours=24)

        diff = nxt - now

        return diff.total_seconds()

    def start_timer(self, call_back:Callable[[Any],Any]):
        #TODO: support args.
        diff = self._get_diff()

        print("DEBUG", diff)

        self.timer = threading.Timer(diff, call_back)
        self.timer.daemon = True
        self.timer.start()
        while True:
            if not self.timer.is_alive():
                del self.timer
                self.start_timer(call_back)

    def stop_timer(self):
        self.timer.cancel()

