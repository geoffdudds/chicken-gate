import BlynkLib
from BlynkTimer import BlynkTimer
from gate import Gate


class Api:
    gate: Gate = None
    blynk: BlynkLib.Blynk = None

    def __init__(self, gate: Gate):
        Api.gate = gate
        Api.blynk = BlynkLib.Blynk("3Ngd6Tdw9djI17trS1AfVY5aXfhlBwiz")
        self.time = 0
        self.timer = BlynkTimer()
        self.timer.set_interval(5, self.elapse_5s)

    # Register Virtual Pins
    @blynk.on("V0")
    def v0_gate_cmd_write_handler(value):
        print("V0 gate command: {}".format(value))
        if value == 0:
            Api.gate.lower()
        elif value == 1:
            Api.gate.lift()
        else:
            print("invalid gate command")

    def write_gate_status(status_in_percent):
        Api.gate.virtual_write(1, status_in_percent)

    def elapse_5s(self):
        self.time += 5
        self.blynk.virtual_write(2, self.time)

    def run(self):
        Api.blynk.run()
        self.timer.run()
