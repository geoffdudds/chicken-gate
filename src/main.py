import time

time.sleep(60)

from gate import Gate
from schedule import Schedule
from api import Api
import errno
import email_me


# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL)


def main():

    gate = Gate()
    api = Api(gate)
    schedule = Schedule(gate)

    # todo: init gate position at startup? Maybe schedule can do this?

    print("Started chicken gate")
    # timer = 0

    while True:
        try:
            api.run()
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
