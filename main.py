from gate import Gate
from schedule import Schedule
from api import Api
import errno

# import time

# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL)


def main():
    gate = Gate()
    api = Api(gate)
    schedule = Schedule(gate)

    # todo: init gate position at startup? Maybe schedule can do this?

    # print("entry")
    # timer = 0

    while True:
        # print("time alive: " + str(timer))
        # time.sleep(1)
        # timer = timer + 1

        try:
            api.run()
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass


if __name__ == "__main__":
    main()
