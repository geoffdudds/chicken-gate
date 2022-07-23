from gate import Gate
from schedule import Schedule
from api import Api


def main():
    gate = Gate()

    # todo schedule cannot be blocking
    api = Api(gate)
    schedule = Schedule(gate)

    # init gate position at startup? Maybe schedule can do this?

    while True:
        api.run()


if __name__ == "__main__":
    main()
