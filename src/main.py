import time, threading

time.sleep(60)

from gate import Gate
from schedule import Schedule
from api import Api
from gate_drv import Gate_drv
import errno
import email_me


# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL)

tick_100ms = 0


def elapse_100ms():
    global tick_100ms
    tick_100ms += 1


def main():
    gate = Gate()
    api = Api(gate)
    schedule = Schedule(gate)
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
                if api_cmd == api.Cmd.OPEN:
                    gate_drv.open()
                elif api_cmd == api.Cmd.CLOSE:
                    gate_drv.close()

                # todo: make the command an enum class on its on in a file
                # todo: remove more threads? consider mutexes?
                # note: will need separate thread for schedule
                # next: make into one thread then test manual

                gate_drv.tick()
                api.set_position(gate_drv.get_posn())

        except IOError as e:
            if e.errno == errno.EPIPE:
                print("Caught pipe error - restarting...")
                email_me.send_email("Pipe error")
                print(e)
            else:
                print("Caught unhandled exception - not restarting")
                email_me.send_email("Some other error")
                print(e)


if __name__ == "__main__":
    main()
