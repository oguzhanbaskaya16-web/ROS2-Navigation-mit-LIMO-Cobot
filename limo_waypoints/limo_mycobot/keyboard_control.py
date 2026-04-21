from pymycobot.mycobot import MyCobot
import time

PORT = "/dev/ttyACM0"
BAUD = 115200
STEP = 5      # Grad pro Tastendruck
SPEED = 20    # eher langsam und sicher

def clamp(value, low, high):
    return max(low, min(high, value))

def init_arm(mc):
    print("Initialisiere Arm...")
    mc.release_all_servos()
    time.sleep(2)
    mc.power_on()
    time.sleep(2)
    mc.set_fresh_mode(1)
    time.sleep(1)
    print("Arm bereit.")

    mc.send_angles([0, -20, 20, 0, 0, 0], 20)
    time.sleep(5)

def wait_until_done(mc, timeout=10):
    for _ in range(timeout * 10):
        time.sleep(0.1)
        if mc.is_moving() == 0:
            break

def print_pose(mc):
    angles = mc.get_angles()
    coords = mc.get_coords()
    print("\nAktuelle Winkel:", angles)
    print("Aktuelle Koordinaten:", coords)

def move_joint(mc, joint_index, delta):
    angles = mc.get_angles()
    if not angles:
        print("Konnte Winkel nicht lesen.")
        return

    target = angles[:]
    target[joint_index] = clamp(target[joint_index] + delta, -170, 170)

    print(f"Bewege Gelenk {joint_index + 1} auf {target[joint_index]:.2f}°")
    mc.send_angles(target, SPEED)
    wait_until_done(mc)
    print_pose(mc)

def home(mc):
    print("Fahre Home...")
    mc.send_angles([0, 0, 0, 0, 0, 0], SPEED)
    wait_until_done(mc)
    print_pose(mc)

def main():
    mc = MyCobot(PORT, BAUD)
    time.sleep(2)
    init_arm(mc)
    print_pose(mc)

    print("""
Steuerung:
  1 / q  -> Gelenk 1 - / +
  2 / w  -> Gelenk 2 - / +
  3 / e  -> Gelenk 3 - / +
  4 / r  -> Gelenk 4 - / +
  5 / t  -> Gelenk 5 - / +
  6 / z  -> Gelenk 6 - / +
  p      -> Pose ausgeben
  h      -> Home
  x      -> Beenden
""")

    while True:
        cmd = input("Taste eingeben: ").strip().lower()

        if cmd == "1":
            move_joint(mc, 0, -STEP)
        elif cmd == "q":
            move_joint(mc, 0, STEP)
        elif cmd == "2":
            move_joint(mc, 1, -STEP)
        elif cmd == "w":
            move_joint(mc, 1, STEP)
        elif cmd == "3":
            move_joint(mc, 2, -STEP)
        elif cmd == "e":
            move_joint(mc, 2, STEP)
        elif cmd == "4":
            move_joint(mc, 3, -STEP)
        elif cmd == "r":
            move_joint(mc, 3, STEP)
        elif cmd == "5":
            move_joint(mc, 4, -STEP)
        elif cmd == "t":
            move_joint(mc, 4, STEP)
        elif cmd == "6":
            move_joint(mc, 5, -STEP)
        elif cmd == "z":
            move_joint(mc, 5, STEP)
        elif cmd == "p":
            print_pose(mc)
        elif cmd == "h":
            home(mc)
        elif cmd == "x":
            print("Beende Programm.")
            break
        else:
            print("Unbekannte Eingabe.")

if __name__ == "__main__":
    main()