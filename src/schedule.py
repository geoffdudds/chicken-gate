from apscheduler.schedulers.background import BackgroundScheduler
from gate_cmd import Cmd
from suntimes import SunTimes

import os


class Schedule:
    def __init__(self):
        self.__dawn = None
        self.__dusk = None
        self.__lift_job = None
        self.__lower_job = None
        self.gate_cmd = Cmd.NONE
        self.__add_to_log("Program started")

        # create schedule, add job to update dawn / dusk times, and start the scheduler
        self.__suntime = SunTimes()
        self.__sched = BackgroundScheduler()
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

    def __add_to_log(self, entry):
        print(entry)

    def __restart_service(self):
        # required for blynk to keep working
        os.system("/usr/bin/systemctl restart chicken-gate.service")

    def __update_schedule(self):
        self.__update_dawn_and_dusk_times()
        self.__schedule_close()
        self.__schedule_open()

        self.__sched.print_jobs()

    def __update_dawn_and_dusk_times(self):
        self.__dawn = self.__suntime.get_dawn()
        self.__dusk = self.__suntime.get_dusk()

    def __close(self):
        self.__add_to_log("Executing scheduled close job...")
        self.gate_cmd = Cmd.CLOSE

    def __open(self):
        self.__add_to_log("Executing scheduled open job...")
        self.gate_cmd = Cmd.OPEN

    def __schedule_close(self):
        lift_time = self.__dusk
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
            hour=self.__dawn.hour,
            minute=self.__dawn.minute,
        )
