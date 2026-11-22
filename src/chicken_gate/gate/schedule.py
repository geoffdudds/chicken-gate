import subprocess  # nosec B404

from apscheduler.schedulers.background import BackgroundScheduler

from .gate_cmd import Cmd
from .suntimes import SunTimes


class Schedule:
    def __init__(self):
        self.__open_time = None
        self.__close_time = None
        self.__lift_job = None
        self.__lower_job = None
        self.__sun_times = {}
        self.gate_cmd = Cmd.NONE
        self.__add_to_log("Program started")

        # create schedule, add job to update dawn / dusk times, and start the scheduler
        self.__suntime = SunTimes()
        # APScheduler skips jobs that start more than 1 s late by default, which
        # a busy Pi Zero can easily miss, leaving the gate unmoved for the day.
        self.__sched = BackgroundScheduler(
            job_defaults={"misfire_grace_time": 600, "coalesce": True}
        )
        self.__update_sched_job = self.__sched.add_job(
            func=self.__update_schedule,
            trigger="cron",
            replace_existing=True,
            id="0",
            hour=0,
            minute=0,
        )
        self.__update_schedule()
        self.__sched.start()

    def get_gate_cmd(self):
        gate_cmd = self.gate_cmd
        self.gate_cmd = None
        return gate_cmd

    def get_schedule_info(self):
        """Get comprehensive schedule information for the web interface.

        Uses sun times cached at the last schedule update; this is called every
        tick, and recomputing them each time saturates the Pi Zero's CPU.
        """
        sun_times = self.__sun_times
        return {
            "dawn": sun_times["dawn"].isoformat(),
            "dusk": sun_times["dusk"].isoformat(),
            "sunrise": sun_times["sunrise"].isoformat(),
            "sunset": sun_times["sunset"].isoformat(),
            "gate_open_time": self.__open_time.strftime("%H:%M")
            if self.__open_time
            else "Unknown",
            "gate_close_time": self.__close_time.strftime("%H:%M")
            if self.__close_time
            else "Unknown",
            "next_update": "00:00 (midnight)",
        }

    def __add_to_log(self, entry):
        print(entry)

    def __restart_service(self):
        # restart the service to pick up any changes
        try:
            # Secure subprocess call with fixed arguments
            subprocess.run(
                ["/usr/bin/systemctl", "restart", "chicken-gate.service"],  # nosec B603
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to restart service: {e}")
        except FileNotFoundError:
            print("systemctl not found - not running on systemd system")

    def __update_schedule(self):
        self.__update_open_and_close_times()
        self.__schedule_close()
        self.__schedule_open()

        self.__sched.print_jobs()

    def __update_open_and_close_times(self):
        self.__sun_times = self.__suntime.get_times()
        self.__open_time = self.__sun_times["sunrise"]
        self.__close_time = self.__sun_times["dusk"]

    def __close(self):
        self.__add_to_log("Executing scheduled close job...")
        self.gate_cmd = Cmd.CLOSE

    def __open(self):
        self.__add_to_log("Executing scheduled open job...")
        self.gate_cmd = Cmd.OPEN

    def __schedule_close(self):
        if self.__lift_job is not None:
            self.__lift_job.remove()
        self.__lift_job = self.__sched.add_job(
            func=self.__close,
            trigger="cron",
            replace_existing=True,
            id="1",
            hour=self.__close_time.hour,
            minute=self.__close_time.minute,
        )

    def __schedule_open(self):
        if self.__lower_job is not None:
            self.__lower_job.remove()
        self.__lower_job = self.__sched.add_job(
            func=self.__open,
            trigger="cron",
            replace_existing=True,
            id="2",
            hour=self.__open_time.hour,
            minute=self.__open_time.minute,
        )
