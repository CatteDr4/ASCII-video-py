#! /bin/python3
import _curses
import argparse
import curses
import json
import math
import time
import os, sys

vid = None
colored = None

###### VIDEO PARSING ######


def ParseVideo(file):
    with open(file, "r") as f:
        mov = json.loads(f.read())

    global colored
    colored = mov['isColored']
    return mov['name'], mov['FPS'], mov['frames']

###### PLAY VIDEO ######


def PlayVideo(fps, frames):
    ftime = CalcFrameTime(fps)
    for i in frames:
        os.system('clear')
        sys.stdout.write(i)
        time.sleep(ftime)

    """TODO: IMPLEMENT"""

###### OTHER ######


def CalcFrameTime(fps):
    frame_time = 1/fps
    return round_down(frame_time, 3)


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

##### MAIN ######


def main():
    global vid, colored
    parser = argparse.ArgumentParser(description="ASCII movie player")
    parser.add_argument('--file', '-f', dest="file", required=True, help="File to play")

    args = parser.parse_args()

    file = args.file

    vid = ParseVideo(file)
    if colored:
        print(f"""
Name: {vid[0]}
FPS: {vid[1]}
Frame amount: {len(vid[2])}
""")
        input("Press enter to start playing.")
        PlayVideo(vid[1], vid[2])
        input("Finished, press enter to exit")
        os._exit(0)
    else:
        curses.wrapper(curses_main)


def curses_main(stdscr):
    global vid
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.noecho()
    curses.cbreak()
    h, w = stdscr.getmaxyx()
    name, fps, frames = vid
    stdscr.addstr(2, 2, f"Name: {name}")
    stdscr.addstr(4, 2, f"FPS: {fps}")
    stdscr.addstr(6, 2 , f"Frame amount: {len(frames)}")
    x = w//2 - len("Press anything to start playing")//2
    y = h//2
    stdscr.addstr(y, x, "Press anything to start playing")
    stdscr.refresh()
    ftime = CalcFrameTime(fps)
    if stdscr.getch():
        stdscr.clear()
        for i in frames:
            try:
                #if stdscr.getch() == curses.KEY_BACKSPACE:
                    #stdscr.clear()
                    #stdscr.addstr(h//2, w//2 - len("PAUSED"), "PAUSED")
                    #stdscr.refresh()
                    #stdscr.getch()
                stdscr.addstr(0, 0, i)
            except _curses.error:
                stdscr.clear()
                stdscr.addstr(0,0,"Term window is too small.")
                stdscr.getch()
                stdscr.clear()
                os._exit(0)

            time.sleep(ftime)
            stdscr.refresh()
    stdscr.clear()
    stdscr.addstr(h//2, w//2 - len("Finished. Press enter to exit"), "Finished. Press enter to exit")
    if stdscr.getch():
        stdscr.clear()
        os._exit(0)


if __name__ == '__main__':
    main()
