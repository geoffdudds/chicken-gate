import BlynkLib
from BlynkTimer import BlynkTimer

# Initialize Blynk
blynk = BlynkLib.Blynk("3Ngd6Tdw9djI17trS1AfVY5aXfhlBwiz")
time = 0


def elapse_5s():
    global time
    time += 5
    blynk.virtual_write(2, time)


timer = BlynkTimer()
timer.set_interval(5, elapse_5s)

# Register Virtual Pins
@blynk.on("V0")
def my_write_handler(value):
    print("Current V1 value: {}".format(value))
    blynk.virtual_write(1, int(value.pop()))


# def my_read_handler():
#     # this widget will show some time in seconds..
#     blynk.virtual_write(2, int(time.time()))

while True:
    blynk.run()
    timer.run()
