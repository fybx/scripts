#!/usr/bin/env python3
#
#       Ferit Yiğit BALABAN <f@fybx.dev>, 2022
#
from datetime import datetime as dt
from subprocess import run
import shlex
import subprocess
import random
import sys
import os

START_NIGHT = "22.30"
START_DAY = "8.20"
PATH_SCPT_KEYBRD = "$HOME/scripts/keyboard"
PATH_SCPT_LOCKER = "$HOME/scripts/wait_unlock.sh"
PATH_RESC_VOLUME = "$HOME/.config/navi/volume"
PATH_RESC_KBDLGT = "$HOME/.config/navi/keyboard"
PATH_RESC_SCRLGT = "$HOME/.config/navi/screen"
PATH_RESC_LIGHTW = "$HOME/sources/wallpapers/light/"
PATH_RESC_DARKW = "$HOME/sources/wallpapers/dark/"
PATH_RESC_WALLPS = "$HOME/.config/navi/wallpapers"
VAR_KBDNAME = "asus::kbd_backlight"


def set_brightness(device: int, value: int, save_state=False):
    state_kbdlgt = get_brightness(1)
    state_scrlgt = get_brightness(0)
    if value == -1:
        with open(os.path.expandvars(PATH_RESC_SCRLGT if device == 0 else PATH_RESC_KBDLGT), 'r') as f:
            value = int(f.read())
            f.close()
    command = f"brightnessctl set {value}%" if device == 0 else f"brightnessctl --device {VAR_KBDNAME} set {value}%"
    open_subprocess(command)
    if save_state:
        with open(os.path.expandvars(PATH_RESC_SCRLGT if device == 0 else PATH_RESC_KBDLGT), 'w') as f:
            f.write(str(state_scrlgt if device == 0 else state_kbdlgt))
            f.close()


def connect_keyboard():
    command = 'bash ' + PATH_SCPT_KEYBRD
    open_subprocess(command)


def set_volume(value: int, save_state=False):
    state = get_volume()
    if value == -1:
        with open(os.path.expandvars(PATH_RESC_VOLUME), 'r') as f:
            value = int(f.read())
            f.close()
    value = 100 if value > 100 else 0 if value < 0 else value
    command = f'pactl set-sink-volume @DEFAULT_SINK@ {value}%'
    open_subprocess(command)
    if save_state:
        with open(os.path.expandvars(PATH_RESC_VOLUME), 'w') as f:
            f.write(str(state))
            f.close()


def open_subprocess(cmd: str):
    subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def change_wallpaper(mode: int, cringe=False):
    if not os.path.exists(PATH_RESC_WALLPS):
        get_wallpapers()
    region = f"{mode}{1 if cringe else 0}"
    with open(PATH_RESC_WALLPS, 'r') as f:
        file = f.read()
        f.close()
    list = file.split(region)[1].split("EOR")[0].lstrip('\n').splitlines()
    wallpaper = random.choice(list)
    command = f"wal -i {wallpaper}"
    open_subprocess(command)
    command = f"betterlockscreen -u {wallpaper}"
    open_subprocess(command)


def lock():
    open_subprocess(f"bash {PATH_SCPT_LOCKER}")
    open_subprocess(f"betterlockscreen --lock --off 5")


def pause_media():
    if run(["playerctl", "status"], text=True, capture_output=True).stdout == "Playing":
        run(["playerctl", "pause"], text=True, capture_output=True)


def get_wallpapers():
    l0 = os.listdir(PATH_RESC_LIGHTW)
    d0 = os.listdir(PATH_RESC_DARKW)
    l0.remove('cringe')
    d0.remove('cringe')
    l0 = [PATH_RESC_LIGHTW + x + '\n' for x in l0]
    d0 = [PATH_RESC_DARKW + x + '\n' for x in d0]
    l1 = os.listdir(PATH_RESC_LIGHTW + "cringe/")
    d1 = os.listdir(PATH_RESC_DARKW + "cringe/")
    l1 = [PATH_RESC_LIGHTW + "cringe/" + x + '\n' for x in l1]
    d1 = [PATH_RESC_DARKW + "cringe/" + x + '\n' for x in d1]
    with open(PATH_RESC_WALLPS, 'w') as f:
        f.write("00:\n")
        f.writelines(l0)
        f.write("EOR\n01:\n")
        f.writelines(l1)
        f.write("EOR\n10:\n")
        f.writelines(d0)
        f.write("EOR\n11:\n")
        f.writelines(d1)
        f.write("EOR")
        f.close()


def get_brightness(device: int):
    if device == 0:
        cmd = ['brightnessctl']
    elif device == 1:
        cmd = ['brightnessctl', '--device', VAR_KBDNAME]
    return int(run(cmd, text=True, capture_output=True).stdout.split('(')[1].split(')')[0].replace('%', ''))


def get_volume():
    r = run(["pactl", "list"], text=True, capture_output=True)
    for x in r.stdout.split("Sink #0")[1].split("Base Volume:")[0].split(' '):
        if '%' in x:
            return int(x.replace('%', ''))


def log(message: str):
    with open(os.path.expandvars("$HOME/navi.log"), 'a') as f:
        f.write(f"[{dt.now().strftime('%m/%d/%y-%H.%M.%S')}] {message}\n")
        f.close()


def get_hour():
    if 0 <= dt.now().minute <= 9:
        return f"{dt.now().hour}.0{dt.now().minute}"
    return f"{dt.now().hour}.{dt.now().minute}"


def get_hour_spec(hour_str=None):
    if hour_str is not None:
        return (int(hour_str.split('.')[0]) * 60) + int(hour_str.split('.')[0])
    else:
        return (dt.now().hour * 60) + dt.now().minute


def get_mode():
    low = get_hour_spec(START_DAY)
    now = get_hour_spec()
    hgh = get_hour_spec(START_NIGHT)
    return 0 if low <= now < hgh else 1


def expand_vars():
    global PATH_SCPT_KEYBRD
    global PATH_SCPT_LOCKER
    global PATH_RESC_VOLUME
    global PATH_RESC_KBDLGT
    global PATH_RESC_SCRLGT
    global PATH_RESC_LIGHTW
    global PATH_RESC_DARKW
    global PATH_RESC_WALLPS
    PATH_SCPT_KEYBRD = os.path.expandvars(PATH_SCPT_KEYBRD)
    PATH_SCPT_LOCKER = os.path.expandvars(PATH_SCPT_LOCKER)
    PATH_RESC_VOLUME = os.path.expandvars(PATH_RESC_VOLUME)
    PATH_RESC_KBDLGT = os.path.expandvars(PATH_RESC_KBDLGT)
    PATH_RESC_SCRLGT = os.path.expandvars(PATH_RESC_SCRLGT)
    PATH_RESC_LIGHTW = os.path.expandvars(PATH_RESC_LIGHTW)
    PATH_RESC_DARKW = os.path.expandvars(PATH_RESC_DARKW)
    PATH_RESC_WALLPS = os.path.expandvars(PATH_RESC_WALLPS)


def main():
    sys.argv.remove(sys.argv[0])
    sys.argv.reverse()
    expand_vars()
    mode = get_mode()
    if len(sys.argv) == 1:
        if sys.argv[0] == "--login":
            log("modeset2 started with \"--login\"")
            connect_keyboard()
            set_volume(0)
            if mode == 0:
                set_brightness(0, 70)
                set_brightness(1, 0)
            else:
                set_brightness(0, 40)
                set_brightness(1, 100)
            change_wallpaper(mode)
        elif sys.argv[0] == "--lock":
            log("modeset2 started with \"--lock\"")
            set_volume(0, save_state=True)
            set_brightness(0, 0, save_state=True)
            set_brightness(1, 0, save_state=True)
            pause_media()
            lock()
        elif sys.argv[0] == "--unlock":
            log("modeset2 started with \"--unlock\"")
            set_volume(-1)
            set_brightness(0, -1)
            set_brightness(1, -1)
        elif sys.argv[0] == "--shutdown":
            log("modeset2 started with \"--shutdown\"")
            print("Shutdown")
        elif sys.argv[0] == "--wallc":
            log("modeset started with \"--wallc\"")
            change_wallpaper(mode, cringe=True)
        elif sys.argv[0] == "--wallp":
            log("modeset started with \"--wallp\"")
            change_wallpaper(mode)
    elif len(sys.argv) == 0:
        print("modeset2 by fyb")
        print(f"local machine time:  {get_hour()}")
        print(f"current mode is:     {get_mode()}")
        print(f"current sink volume: {get_volume()}")
        print("""Available options:
1. Login
2. Lock
3. Unlock
4. Shutdown
5. Wallpaper (Make me cringe)
6. Wallpaper (Panic mode on)""")
    else:
        print("Issuing more than 1 argument to modeset2 is not supported yet. Aborting...")
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
