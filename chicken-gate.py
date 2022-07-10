from suntime import Sun
from dateutil import tz
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from gate import Gate


class ChickenGate:
    def __init__(self):
        self.sunrise = None
        self.sunset = None
        self.lift_job = None
        self.lower_job = None
        self.add_to_log("Program started")
        self.gate = Gate()

        # create schedule, add job to update sunrise / sunset times, and start the scheduler
        self.sched = BlockingScheduler()
        self.update_sched_job = self.sched.add_job(
            func=self.update_schedule,
            trigger="cron",
            hour=0,
            minute=0,
        )
        self.update_schedule()
        self.sched.start()

    def add_to_log(self, entry):
        now = datetime.now()
        time = now.strftime("%Y/%m/%d - %H:%M:%S")
        with open("log.txt", "a+") as f:
            f.write(time + ": " + entry)
            f.write("\n")

    def update_schedule(self):
        self.update_sunrise_sunset_times()
        self.schedule_lift()
        self.schedule_lower()

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
        self.sunrise = sunrise_utc.astimezone(to_zone)

        # repeat for sunset time
        sunset_utc = sun.get_sunset_time()
        self.sunset = sunset_utc.astimezone(to_zone)

    def lift(self):
        self.add_to_log("Executing lift job...")
        self.gate.lift()

    def lower(self):
        self.add_to_log("Executing lower job...")
        self.gate.lower()

    def schedule_lift(self):
        if self.lift_job is not None:
            self.lift_job.remove()
        self.lift_job = self.sched.add_job(
            func=self.lift,
            trigger="cron",
            hour=self.sunset.hour,
            minute=self.sunset.minute,
        )

        msg = "Gate scheduled to lift at {}".format(self.sunset.strftime("%H:%M"))
        print(msg)
        self.add_to_log(msg)

    def schedule_lower(self):
        if self.lower_job is not None:
            self.lower_job.remove()
        self.lower_job = self.sched.add_job(
            func=self.lower,
            trigger="cron",
            hour=self.sunrise.hour,
            minute=self.sunrise.minute,
        )

        msg = "Gate scheduled to lower at {}".format(self.sunrise.strftime("%H:%M"))
        print(msg)
        self.add_to_log(msg)


def main():
    chicken_gate = ChickenGate()


if __name__ == "__main__":
    main()
