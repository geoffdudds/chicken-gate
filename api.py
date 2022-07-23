import BlynkLib
from BlynkTimer import BlynkTimer


class Api:
    def __init__(self):
        self.blynk = BlynkLib.Blynk("3Ngd6Tdw9djI17trS1AfVY5aXfhlBwiz")
        self.time = 0
        self.timer = BlynkTimer()
        self.timer.set_interval(5, self.elapse_5s)

        # Register Virtual Pins
        @self.on("V0")
        def my_write_handler(value):
            print("Current V1 value: {}".format(value))
            self.virtual_write(1, int(value.pop()))

    def elapse_5s(self):
        self.time += 5
        self.blynk.virtual_write(2, self.time)

    def run(self):
        self.blynk.run()
        self.timer.run()
