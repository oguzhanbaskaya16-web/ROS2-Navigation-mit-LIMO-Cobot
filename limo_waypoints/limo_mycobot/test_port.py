from pymycobot.mycobot import MyCobot
import time

tests = [
    ("/dev/ttyUSB0", 115200),
    ("/dev/ttyACM0", 115200),
    ("/dev/ttyUSB0", 1000000),
    ("/dev/ttyACM0", 1000000),
]

for port, baud in tests:
    try:
        print(f"\nTeste {port} @ {baud}")
        mc = MyCobot(port, baud)
        time.sleep(2)
        print("angles:", mc.get_angles())
        print("coords:", mc.get_coords())
        print("is_power_on:", mc.is_power_on())
    except Exception as e:
        print("Fehler:", e)