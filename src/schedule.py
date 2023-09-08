from gate_cmd import Cmd
from suntime import Sun
from dateutil import tz
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os


class Schedule:
    def __init__(self):
        self.__sunrise = None
        self.__sunset = None
        self.__lift_job = None
        self.__lower_job = None
        self.gate_cmd = Cmd.NONE
        self.__add_to_log("Program started")

        # create schedule, add job to update sunrise / sunset times, and start the scheduler
        self.__sched = BackgroundScheduler()
        self.__update_sched_job = self.__sched.add_job(
            func=self.__restart_service,
            trigger="cron",
            replace_existing=True,
            id="0",
            hour=12,
            minute=0,
        )
        self.__update_schedule()
        self.__sched.start()

    def get_gate_cmd(self):
        gate_cmd = self.gate_cmd
        self.gate_cmd = None
        return gate_cmd

    def __add_to_log(self, entry):
        print(entry)

    def __restart_service(self):
        # required for blynk to keep working
        os.system("/usr/bin/systemctl restart chicken-gate.service")

    def __update_schedule(self):
        self.__update_sunrise_sunset_times()
        self.__schedule_close()
        self.__schedule_open()

        self.__sched.print_jobs()

    def __update_sunrise_sunset_times(self):
        latitude = 49.164379
        longitude = -123.936661
        sun = Sun(latitude, longitude)
        to_zone = tz.gettz()

        # get sunrise time
        sunrise_utc = sun.get_sunrise_time()
        self.__sunrise = sunrise_utc.astimezone(to_zone)

        # repeat for sunset time
        sunset_utc = sun.get_sunset_time()
        self.__sunset = sunset_utc.astimezone(to_zone)

    def __close(self):
        self.__add_to_log("Executing scheduled close job...")
        self.gate_cmd = Cmd.CLOSE

    def __open(self):
        self.__add_to_log("Executing scheduled open job...")
        self.gate_cmd = Cmd.OPEN

    def __schedule_close(self):
        lift_time = self.__sunset + timedelta(minutes=30)
        if self.__lift_job is not None:
            self.__lift_job.remove()
        self.__lift_job = self.__sched.add_job(
            func=self.__close,
            trigger="cron",
            replace_existing=True,
            id="1",
            hour=lift_time.hour,
            minute=lift_time.minute,
        )

    def __schedule_open(self):
        if self.__lower_job is not None:
            self.__lower_job.remove()
        self.__lower_job = self.__sched.add_job(
            func=self.__open,
            trigger="cron",
            replace_existing=True,
            id="2",
            hour=self.__sunrise.hour,
            minute=self.__sunrise.minute,
        )
