cursesui.py
===========

A simple Python module to create a text-mode windowing user interface for console (i.e. command-line) apps.

Tested natively on linux Mint 20.3 and a Raspberry PI4 running Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-1082-raspi aarch64), accessed via puTTY.

Your specific terminal capabilities will matter. See the docs for more info.

# Purpose

I developed this because I needed a simple user interface for testing an asynchronous Python app (see pyjacuzzi).

# Features

1. It simplifies creating and maintaining text-based windows based on the standard ncurses library.

2. It allows you to configure default responses to keyboard input (that apply to all windows), and also override those defaults and add new responses on a window-by-window basis.

3. It preserves the ability to use the standard Python logging library without your log messages corrupting the curses windows.

4. It works by design with asychronous processes (i.e those using the Python asyncio library) so your windows can both monitor and control them.

# To Test

1. From the directory where cursesui.py is located, open a terminal and run "python3 cursesui.py". This will run the simplest demo version.

2. If you also have placed demoprocess.py in that same directory, then the demonstration will also run two separate ("slow" and "fast") asynchronous processes concurrently that you can monitor and control. Note incidentally that you can also run this version of the demo with the command line "python3 demoprocess.py".

3. The demoprocess.py module is also a simple example of what you will need to do to integrate cursesui.py into your own project.

# Disclaimers

1. While I am not new to programming, I am relatively new to Python, git and Github -- so please be nice!  I welcome your corrections, suggestions, improvements, and feedback (particularly when it is constructive).

2. If you are one of those folks who love sparse code without comments, you will be disappointed. Sorry (not sorry).

