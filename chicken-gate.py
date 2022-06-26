from suntime import Sun
from dateutil import tz
from apscheduler.schedulers.blocking import BlockingScheduler


class ChickenGate:
    def __init__(self):
        self.sunrise = None
        self.sunset = None
        self.lift_job = None
        self.lower_job = None

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

    def update_schedule(self):
        self.update_sunrise_sunset_times()
        self.schedule_lift()
        self.schedule_lower()

        self.sched.print_jobs()

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
        print("executing lift job...")

    def lower(self):
        print("executing lower job...")

    def schedule_lift(self):
        if self.lift_job is not None:
            self.lift_job.remove()
        self.lift_job = self.sched.add_job(
            func=self.lift,
            trigger="cron",
            hour=self.sunset.hour,
            minute=self.sunset.minute,
        )

        print("Gate schedule to lift at {}".format(self.sunset.strftime("%H:%M")))

    def schedule_lower(self):
        if self.lower_job is not None:
            self.lower_job.remove()
        self.lower_job = self.sched.add_job(
            func=self.lower,
            trigger="cron",
            hour=self.sunrise.hour,
            minute=self.sunrise.minute,
        )

        print("Gate schedule to lower at {}".format(self.sunrise.strftime("%H:%M")))


def main():
    chicken_gate = ChickenGate()


if __name__ == "__main__":
    main()
