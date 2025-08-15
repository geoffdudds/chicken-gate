import time as tm


class Timer:
    def __init__(self):
        self.__start_time = None
        self.__last_read = None

    def start(self):
        now = tm.perf_counter()
        self.__start_time = now
        self.__last_read = now

    def get_time(self):
        now = tm.perf_counter()
        self.__last_read = now
        return now - self.__start_time

    def has_elapsed(self, time):
        return (tm.perf_counter() - self.__start_time) > time

    def get_since_last_read(self):
        now = tm.perf_counter()
        time_since_last_read = now - self.__last_read
        self.__last_read = now
        return time_since_last_read
