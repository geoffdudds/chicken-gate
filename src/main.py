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
tick_sum = 0


def elapse_100ms():
    global tick_100ms
    global tick_sum
    tick_100ms += 1
    tick_sum += 1
    if tick_sum > 10:
        print("1s elapsed in main tick")
        tick_sum = 0


def main():
    global tick_100ms
    gate = Gate()
    gate_drv = Gate_drv(gate)
    api = Api()
    schedule = Schedule()

    threading.Timer(0.1, elapse_100ms).start()

    print("Started chicken gate")

    while True:
        try:
            api.run()

            while tick_100ms > 0:
                tick_100ms -= 1
                
                # push api commands to driver
                gate_drv.reset_posn_to(api.get_posn_reset())
                api_cmd = api.get_cmd()
                if api_cmd == Cmd.OPEN:
                    print("app cmd to open gate")
                    gate_drv.open()
                elif api_cmd == Cmd.CLOSE:
                    print("app cmd to close gate")
                    gate_drv.close()

                # push api commands to driver
                sched_cmd = schedule.get_gate_cmd()
                if sched_cmd == Cmd.OPEN:
                    print("sched cmd to open gate")
                    gate_drv.open()
                elif sched_cmd == Cmd.CLOSE:
                    print("sched cmd to close gate")
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
