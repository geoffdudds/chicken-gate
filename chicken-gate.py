# need to periodaically check time then raise or lower the gate


from datetime import datetime
from suntime import Sun, SunTimeException
from dateutil import tz


# get sunrise, sunset
latitude = 49.164379
longitude = -123.936661
sun = Sun(latitude, longitude)


# Get today's sunrise and sunset in UTC
today_sr = sun.get_sunrise_time()
today_ss = sun.get_sunset_time()

from_zone = tz.gettz("UTC")
to_zone = tz.gettz()
today_sr = today_sr.replace(tzinfo=from_zone)
local_sr = today_sr.astimezone(to_zone)
today_ss = today_ss.replace(tzinfo=from_zone)
local_ss = today_ss.astimezone(to_zone)

print(
    "Today at Nanaimo the sun raised at {} and get down at {} local time".format(
        local_sr.strftime("%H:%M"), local_ss.strftime("%H:%M")
    )
)

# get time
now = datetime.now()

print("Time in Nanimo is {}".format(now.strftime("%H:%M")))

# if time is after between sunrise and senset, gate is open
# otherwise, its closed
