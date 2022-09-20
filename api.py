import BlynkLib
from BlynkTimer import BlynkTimer
from gate import Gate


class Api:
    gate: Gate = None
    blynk: BlynkLib.Blynk = None

    def __init__(self, gate: Gate):
        Api.gate = gate
        Api.gate.set_position_fbk_cb(self.write_gate_status)
        Api.blynk = BlynkLib.Blynk("3Ngd6Tdw9djI17trS1AfVY5aXfhlBwiz")
        self.time = 0
        self.timer = BlynkTimer()
        self.timer.set_interval(5, self.elapse_5s)

        # Register Virtual Pins
        @Api.blynk.on("V0")
        def v0_gate_cmd_write_handler(value):
            print("V0 gate command: {}".format(value))
            val = value.pop()
            if val == "0":
                Api.gate.lower()
            elif val == "1":
                Api.gate.lift()
            else:
                print("invalid gate command")

    def write_gate_status(client, status_in_percent):
        Api.blynk.virtual_write(3, status_in_percent)

    def elapse_5s(self):
        self.time += 5
        self.blynk.virtual_write(2, self.time)
        # print("time alive: " + str(self.time))

    def run(self):
        Api.blynk.run()
        self.timer.run()
