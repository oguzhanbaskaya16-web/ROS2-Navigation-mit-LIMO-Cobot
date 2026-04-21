from pymycobot.mycobot import MyCobot
import time

mc = MyCobot('/dev/ttyACM0', 115200)
time.sleep(2)

print("Start angles:", mc.get_angles())
print("Power:", mc.is_power_on())

# 🔥 WICHTIG: Reset durchführen
print("Release servos...")
mc.release_all_servos()
time.sleep(2)

print("Power on...")
mc.power_on()
time.sleep(2)

print("Set fresh mode...")
mc.set_fresh_mode(1)
time.sleep(1)

print("Angles nach Reset:", mc.get_angles())

# 🚀 Bewegung testen
print("Sende Bewegung...")
mc.send_angles([0, -30, 30, 0, 0, 0], 40)

for i in range(10):
    time.sleep(1)
    print(f"t={i+1}s moving:", mc.is_moving(), " angles:", mc.get_angles())