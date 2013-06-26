#!/usr/bin/env python

"""

Release under the terms of the GPL licence
You can get a copy of the license at http://www.gnu.org

Ported by: Matt Hersant (matt_hersant[at]yahoo[dot]com)

Description: An animated ascii art fire.
To force no color: shell> TERM=vt100 ./asciifire.py

This algorithm was ported from javascript written by: Thiemo Mattig
http://maettig.com/code/javascript/asciifire.html

"""

import sys
import curses
import optparse
from random import random
from time import time, sleep
from signal import signal, SIGINT

##############################################
def get_options():
##############################################
    # Process command line options
    OptionParser = optparse.OptionParser
    parser = OptionParser()
    parser.add_option(                        \
        '-b',                                 \
        '--block',                            \
        action = 'store_true',                \
        dest   = 'block',                     \
        help   = 'Enable blocking getch mode' \
    )
    parser.add_option(                        \
        '-s',                                 \
        '--cycle',                            \
        action ='store_true',                 \
        dest   ='cycle',                      \
        help   ='Cycle ascii colors'          \
    )
    parser.add_option(                        \
        '-t',                                 \
        '--cycletime',                        \
        type = 'int',                         \
        dest = 'cycle_time',                  \
        help = 'Cycle time interval'          \
    )
    parser.add_option(                        \
        '-d',                                 \
        '--delay',                            \
        type    = 'int',                      \
        dest    = 'delay',                    \
        default = 18750,                      \
        help    = 'Delay time in seconds. Will be divided by 1000000'\
    )
    parser.add_option(                        \
        '-c',                                 \
        '--color',                            \
        type    = 'string',                   \
        dest    = 'color',                    \
        default = 'RED',                      \
        help    = 'Specify ascii color'       \
    )

    (options, args) = parser.parse_args()

    # If the human specifies a cycle_time, they must want to cycle.
    if options.cycle_time:
        options.cycle = True

    # Set default cycle time.
    if not options.cycle_time:
        options.cycle_time = 15

    # Valid colors.
    options.validcolors = { 'RED':1, 'BLUE':2, 'GREEN':3, 'YELLOW':4, 'WHITE': 5 }
    if options.color != 'RED':
        options.color = options.color.upper()
        if not options.validcolors.get(options.color):
            # Human specified bad color.. using RED.
            options.color = 'RED'

    return (options, args)

##############################################
def signal_handler(signal, frame):
##############################################
    curses.endwin()
    sys.exit(0)

##############################################
if __name__=='__main__':
##############################################
    (options, args) = get_options()

    # Initialize curses.
    myscreen = curses.initscr()
    curses.noecho()

    # This variable allows dynamic curses colors.
    cursescolor = options.validcolors.get(options.color)

    # Initialize primary colors.
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED,    curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE,   curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN,  curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE,  curses.COLOR_BLACK)
    else:
        cursescolor = ''

    # Handle cycling ascii colors.
    last_cycle_changed = time()

    # Signal handler for sigint
    signal(SIGINT, signal_handler)

    if options.block:
        # Blocking getch().
        myscreen.timeout(-1)
    else:
        # Non-blocking getch().
        myscreen.timeout(0)

    # The dimensions of our ascii art.
    size = 80 * 25

    b = []
    for i in range(size + 81):
        b.append(0)

    # The ascii we will use for our fire.
    char = [' ', '.', ':', '*', 's', 'S', '#', '$']

    # Switch for pause.
    paused = False

    # Infinite loop.
    while True:
        event = myscreen.getch()
        if event == ord('q'):
            # q means human wants to quit.
            break
        if event == ord('p'):
            # p means human wants to pause.
            if not paused:
                myscreen.timeout(-1)
                paused = True
            else:
                myscreen.timeout(0)
                paused = False

        for i in range(10):
            # random() returns a float.
            randval = random() * 80
            # Typecasting to int does a floor().
            b[int(randval) + 80 * 24] = 70

        # a is a two deminsional list.
        a = []
        tmplist = []
        for i in range(size):
            # Purposefully typecast rval as float.
            tmp = float((b[i] + b[i + 1] + b[i + 80] + b[i + 81]) / 4)
            # Typecasting to int does a floor().
            b[i] = int(tmp)

            if b[i] > 7:
                tmplist.append(char[7])
            else:
                tmplist.append(char[b[i]])

            if (i % 80 > 78):
                a.append(tmplist);
                tmplist = []

        # Starting coordinates. Need to programatically determine center.
        x = 25
        y = 5

        # Clear curses buffer.
        myscreen.erase()
        # Populate curses buffer.
        for outerrow in a:
            for innerrow in outerrow:
                # Check to see if term supports colors.
                if curses.has_colors():
                    # Add colorful ascii to curses buffer.
                    myscreen.addstr(y, x, innerrow, curses.color_pair(cursescolor))
                else:
                    # Add colorless ascii to curses buffer.
                    myscreen.addstr(y, x, innerrow)
                # Update x for the next item in the row.
                x += 1

            # We're at the end of a row, update x/y for the next row.
            y += 1
            x = 10


        # Draw/blit curses buffer to screen.
        myscreen.refresh()

        # Handle color cycling.
        if curses.has_colors():
            if options.cycle:
                # Check to see if it's time to change colors.
                if (time() - last_cycle_changed) > options.cycle_time:
                    last_cycle_changed = time()
                    # Change the color.
                    if cursescolor == len(options.validcolors.keys()):
                        cursescolor = 1
                    else:
                        cursescolor += 1


        # Usleep so we don't hog cpu time.
        sleep(options.delay/1000000.0)

    # De-initialize curses, and return terminal to normal status.
    curses.endwin()

# TODO
# add error handling to gracefully exit (endwin) if things break
# validate options.deply...
# (maxX, maxY) = myscreen.getmaxyx() at start and before every blit
# 29 89
# print instructions at bottowm q : quit p : pause

# FIGURE OUT WHY TOP LINE IS SHIFTED TO THE RIGHT
# PLACE ASCII ART INTO A BORDERED WINDOW
# ENSURE WINDOW IS CENTERED
# ENSURE CODE WORKS ON STANDARD TERMINAL SIZE