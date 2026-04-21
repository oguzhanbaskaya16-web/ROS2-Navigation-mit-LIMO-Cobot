from pymycobot.mycobot import MyCobot
import time

mc = MyCobot('/dev/ttyACM0', 115200)
time.sleep(2)

# Reset (wie immer!)
mc.release_all_servos()
time.sleep(2)
mc.power_on()
time.sleep(2)
mc.set_fresh_mode(1)
time.sleep(1)

mc.send_angles([0, -20, 20, 0, 0, 0], 20)
time.sleep(5)

print("Öffne Greifer")
mc.set_gripper_state(0, 50, 1)
time.sleep(3)

print("Schließe Greifer")
mc.set_gripper_state(1, 50, 1)
time.sleep(3)

print("Halb schließen")
mc.set_gripper_value(50, 50)
time.sleep(3)