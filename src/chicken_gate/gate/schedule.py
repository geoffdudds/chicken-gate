import subprocess  # nosec B404
import threading
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from ..shared import settings as user_settings
from .gate_cmd import Cmd
from .suntimes import SunTimes


class Schedule:
    def __init__(self, settings=None):
        self.__settings = dict(settings or user_settings.DEFAULTS)
        self.__lock = threading.Lock()
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
        settings = self.__settings
        return {
            "dawn": sun_times["dawn"].isoformat(),
            "dusk": sun_times["dusk"].isoformat(),
            "sunrise": sun_times["sunrise"].isoformat(),
            "sunset": sun_times["sunset"].isoformat(),
            "gate_open": self.__open_time.isoformat() if self.__open_time else None,
            "gate_close": self.__close_time.isoformat() if self.__close_time else None,
            "open_event": settings["open_event"],
            "open_offset_min": settings["open_offset_min"],
            "close_event": settings["close_event"],
            "close_offset_min": settings["close_offset_min"],
            "gate_open_time": self.__open_time.strftime("%H:%M")
            if self.__open_time
            else "Unknown",
            "gate_close_time": self.__close_time.strftime("%H:%M")
            if self.__close_time
            else "Unknown",
            "next_update": "00:00 (midnight)",
        }

    def apply_settings(self, settings, catch_up=True):
        """Reschedule today's open and close jobs for new event/offset settings.

        A cron job whose time has already passed won't run until tomorrow, so if
        the change moves an event that hasn't happened yet to a time that has,
        run it now (when ``catch_up`` is set) rather than skip it for the day.
        """
        with self.__lock:
            old_open, old_close = self.__open_time, self.__close_time
            self.__settings = dict(settings)
            self.__set_open_and_close_times()
            self.__schedule_close()
            self.__schedule_open()
            new_open, new_close = self.__open_time, self.__close_time

        self.__add_to_log(
            f"Schedule updated: open {new_open:%H:%M}, close {new_close:%H:%M}"
        )
        if not catch_up:
            return
        now = datetime.now(new_close.tzinfo)
        if new_close <= now < old_close:
            self.__add_to_log("New close time has passed; closing now")
            self.gate_cmd = Cmd.CLOSE
        elif new_open <= now < old_open and now < new_close:
            self.__add_to_log("New open time has passed; opening now")
            self.gate_cmd = Cmd.OPEN

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
        with self.__lock:
            self.__sun_times = self.__suntime.get_times()
            self.__set_open_and_close_times()
            self.__schedule_close()
            self.__schedule_open()

        self.__sched.print_jobs()

    def __set_open_and_close_times(self):
        """Derive today's gate times from the cached sun times and settings.

        Seconds are dropped because the cron jobs fire on the minute.
        """
        settings = self.__settings
        self.__open_time = self.__event_time(
            settings["open_event"], settings["open_offset_min"]
        )
        self.__close_time = self.__event_time(
            settings["close_event"], settings["close_offset_min"]
        )

    def __event_time(self, event, offset_min):
        """Offset a sun event, kept within its own day so the daily jobs line up."""
        base = self.__sun_times[event]
        day_start = base.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = base.replace(hour=23, minute=59, second=0, microsecond=0)
        time = (base + timedelta(minutes=offset_min)).replace(second=0, microsecond=0)
        return min(max(time, day_start), day_end)

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
