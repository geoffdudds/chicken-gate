from astral.sun import sun
from astral import LocationInfo
from dateutil import tz

class SunTimes:
    def __init__(self):
        self.__latitude = 49.164379
        self.__longitude = -123.936661
        self.__loc_info = LocationInfo("Nanaimo", "Canada", "pst", self.__latitude , self.__longitude)
        
    def get_dawn(self):
        print(tz.gettz())
        loc_times = sun(self.__loc_info.observer, tzinfo=tz.gettz())
        return loc_times["dawn"]
        
    def get_dusk(self):
        loc_times = sun(self.__loc_info.observer, tzinfo=tz.gettz())
        return loc_times["dusk"]
        
        
