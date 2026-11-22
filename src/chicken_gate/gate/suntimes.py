from astral import LocationInfo
from astral.sun import sun
from dateutil import tz


class SunTimes:
    def __init__(self):
        self.__latitude = 49.164379
        self.__longitude = -123.936661
        self.__loc_info = LocationInfo(
            "Nanaimo", "Canada", "pst", self.__latitude, self.__longitude
        )

    def get_times(self):
        """Return today's dawn, sunrise, sunset and dusk from a single calculation."""
        return sun(self.__loc_info.observer, tzinfo=tz.gettz())
