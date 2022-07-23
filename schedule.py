from suntime import Sun
from dateutil import tz
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from gate import Gate
import time


class Schedule:
    def __init__(self):
        self.sunrise_time = None
        self.sunset_time = None
        self.sunset_job = None
        self.sunrise_job = None
        self.sunrise_cb = None
        self.sunset_cb = None
        self.gate = Gate()
        self.add_to_log("Program started")

        # create schedule, add job to update sunrise / sunset times, and start the scheduler
        self.sched = BlockingScheduler()
        self.update_sched_job = self.sched.add_job(
            func=self.update_schedule,
            trigger="cron",
            hour=0,
            minute=0,
        )
        self.update_schedule()

        # test relay
        while True:
            self.gate.lift()
            time.sleep(2)
            self.gate.lower()
            time.sleep(2)

        self.sched.start()

    def set_sunrise_cb(self, sunrise_cb):
        self.sunrise_cb = sunrise_cb

    def set_sunset_cb(self, sunset_cb):
        self.sunrise_cb = sunset_cb

    def add_to_log(self, entry):
        now = datetime.now()
        time = now.strftime("%Y/%m/%d - %H:%M:%S")
        with open("log.txt", "a+") as f:
            f.write(time + ": " + entry)
            f.write("\n")

    def update_schedule(self):
        self.update_sunrise_sunset_times()
        self.schedule_sunset()
        self.schedule_sunrise()

        self.sched.print_jobs()
        with open("log.txt", "a") as f:
            self.add_to_log("")
            self.sched.print_jobs(out=f)

    def update_sunrise_sunset_times(self):
        latitude = 49.164379
        longitude = -123.936661
        sun = Sun(latitude, longitude)
        to_zone = tz.gettz()

        # get sunrise time
        sunrise_utc = sun.get_sunrise_time()
        self.sunrise_time = sunrise_utc.astimezone(to_zone)

        # repeat for sunset time
        sunset_utc = sun.get_sunset_time()
        self.sunset_time = sunset_utc.astimezone(to_zone)

    def run_sunset_job(self):
        self.add_to_log("Running sunset job...")
        if self.sunset_cb is not None:
            self.sunset_cb()

    def run_sunrise_job(self):
        self.add_to_log("Running sunrise job...")
        if self.sunrise_cb is not None:
            self.sunrise_cb()

    def schedule_sunset(self):
        if self.sunset_job is not None:
            self.sunset_job.remove()
        self.sunset_job = self.sched.add_job(
            func=self.run_sunset_job,
            trigger="cron",
            hour=self.sunset_time.hour,
            minute=self.sunset_time.minute,
        )

        msg = "Gate scheduled to lift at {}".format(self.sunset_time.strftime("%H:%M"))
        print(msg)
        self.add_to_log(msg)

    def schedule_sunrise(self):
        if self.sunrise_job is not None:
            self.sunrise_job.remove()
        self.sunrise_job = self.sched.add_job(
            func=self.run_sunrise_job,
            trigger="cron",
            hour=self.sunrise_time.hour,
            minute=self.sunrise_time.minute,
        )

        msg = "Gate scheduled to lower at {}".format(
            self.sunrise_time.strftime("%H:%M")
        )
        print(msg)
        self.add_to_log(msg)


def main():
    chicken_gate = Schedule()


if __name__ == "__main__":
    main()
