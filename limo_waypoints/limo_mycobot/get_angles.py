from pymycobot.mycobot import MyCobot
mc = MyCobot('/dev/ttyACM0', 115200)
print(mc.get_angles())
print(mc.get_coords())