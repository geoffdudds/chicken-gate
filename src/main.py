import time, threading

time.sleep(60)

from gate import Gate
from schedule import Schedule
from api import Api
from gate_drv import Gate_drv
from gate_cmd import Cmd
import errno
from email_me import send_email


# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL)

tick_100ms = 0


def elapse_100ms():
    global tick_100ms
    tick_100ms += 1


def main():
    gate = Gate()
    api = Api()
    schedule = Schedule()
    gate_drv = Gate_drv()

    threading.Timer(0.1, elapse_100ms).start()

    print("Started chicken gate")

    while True:
        try:
            api.run()

            while elapse_100ms > 0:
                # push api commands to driver
                gate_drv.reset_posn_to(api.get_posn_reset())
                api_cmd = api.get_cmd()
                if api_cmd == Cmd.OPEN:
                    gate_drv.open()
                elif api_cmd == Cmd.CLOSE:
                    gate_drv.close()

                # push api commands to driver
                sched_cmd = schedule.get_gate_cmd()
                if sched_cmd == Cmd.OPEN:
                    gate_drv.open()
                elif sched_cmd == Cmd.CLOSE:
                    gate_drv.close()

                gate_drv.tick()
                api.set_posn(gate_drv.get_posn())

        except IOError as e:
            if e.errno == errno.EPIPE:
                print("Caught pipe error - restarting...")
                send_email("Pipe error")
                print(e)
            else:
                print("Caught unhandled exception - not restarting")
                send_email("Some other error")
                print(e)


if __name__ == "__main__":
    main()
