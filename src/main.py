"""
todo: make the reset gate position use the enum instead of interger
todo: update the gate cmd button when the reset button is pressed
todo: update the gate cmd button when a scheduled cmd is executed
todo: make run as module so imports can work with pytest and program execution
"""


import time, threading

time.sleep(60)

from gate import Gate
from schedule import Schedule
from api import Api
from gate_drv import Gate_drv
from gate_cmd import Cmd
import errno
from email_me import send_email
import os


# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL)

tick_100ms = 0


def elapse_100ms():
    threading.Timer(0.1, elapse_100ms).start()
    global tick_100ms
    tick_100ms += 1


def main():
    global tick_100ms
    pipe_error = False
    other_error = False
    gate = Gate()
    gate_drv = Gate_drv(gate)
    # api = Api()
    schedule = Schedule()
    elapse_100ms()

    print("Started chicken gate")

    while True:
        # if pipe_error is False and other_error is False:
        #     try:
        #         api.run()
        #         pass

        #     except IOError as e:
        #         if e.errno == errno.EPIPE:
        #             print("Caught pipe error")
        #             if pipe_error is False:
        #                 send_email("Pipe error")
        #                 pipe_error = True
        #             print(e)
        #         else:
        #             print("Caught unhandled exception")
        #             if other_error is False:
        #                 send_email("Some other error")
        #                 other_error = True
        #             print(e)

        while tick_100ms > 0:
            tick_100ms -= 1

            # push api commands to driver
            # gate_drv.reset_posn_to(api.get_posn_reset())
            # api_cmd = api.get_cmd()
            # if api_cmd == Cmd.OPEN:
            #     print("app cmd to open gate")
            #     gate_drv.open()
            # elif api_cmd == Cmd.CLOSE:
            #     print("app cmd to close gate")
            #     gate_drv.close()

            # push api commands to driver
            sched_cmd = schedule.get_gate_cmd()
            if sched_cmd == Cmd.OPEN:
                print("sched cmd to open gate")
                gate_drv.open()
            elif sched_cmd == Cmd.CLOSE:
                print("sched cmd to close gate")
                gate_drv.close()

            gate_drv.tick()
            # api.set_posn(gate_drv.get_posn())


if __name__ == "__main__":
    main()
