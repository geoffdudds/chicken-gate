import time
from threading import Thread


class Timer:
    def __init__(self):
        self.time = 0
        self.start_time = 0
        self.target = 0
        # self.timer_thread = Thread(target=self.main)
        # self.cmd_thread.start()

    def set_target(self, target):
        if self.target != target:
            self.time = self.get_time()
            self.target = target
            self.start_time = time.perf_counter()

    def is_at_target(self):
        diff = time.perf_counter() - self.start_time
        sp_change = self.target - self.time
        return abs(diff) > abs(sp_change)

    def get_time(self):
        diff = time.perf_counter() - self.start_time
        sp_change = self.target - self.time
        if sp_change > 0:
            diff = min(diff, sp_change)
        else:
            diff = max(-diff, sp_change)

        return self.time + diff

    def reset(self):
        self.time = 0
        self.start_time = 0
        self.target = 0
