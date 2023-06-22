# This simple demonstration process runs concurrently with the
# CursesUI instance. It simulates an arbitrary external process by
# just changing some of its attribute values at regular intervals.

import asyncio

# These are the specific CursesUI classes that this demo process
# references.
try:
    from cursesui import (CursesUI, log, Align, Textfield, KeyResponse,
                          SubWindow, NewWindow, PadWindow, EditDialog,
                          FloatDialog, EnumDialog)
except ImportError:
    print("Could not find cursesui.py!")
    exit()

import curses.ascii    # Provides useful key value constants

from enum import Enum
import random
import time

class DemoStates(Enum):
    """ enum types for demo State display. In this case
    the values are arbitrary and the enum names are the
    actual strings used to display the current state. Thus
    even though they are constants we won't capitalize them
    here.
    """
    Disconnected = 0
    Idle = 1
    Cycling = 2
    Faulted = 3

class DemoModes(Enum):
    """ enum types for demo's Mode control. For the demo the
    mode names are what the user sees and can choose, while
    the entire enum member is read and written. The enum values
    are arbitrary for this demo test application.
    """
    Disabled = 22
    Setup = 44
    Test = 33
    Run = 11

class DemoProcess:
    """ An example of a simple class for demonstration purposes.
    It defines a coroutine process that runs concurrently with
    the CursesUI process. 
    
    Replace this with your own, real process to use the CursesUI
    class for your application.
    """
    def __init__(self):
        self.current_temperature = 20
        self._temperature_delta = 1
        self.max_temperature = 30
        self.min_temperature = 10
        self.current_state_name = DemoStates.Disconnected.name
        self._state_delay = 5
        self._state_count = self._state_delay
        self.mode = DemoModes.Disabled
        self.demo_red_color = None
        self.demo_green_color = None
        self.demo_blue_color = None
        self.demo_red_delta = None
        self.demo_green_delta = None
        self.demo_blue_delta = None

        # For testing floating point values
        self.current_percent = 0.0
        self._percent_delta = 0.1
        self.max_percent = 1.0
        self.min_percent = -1.0

    def _update_temperature(self):
        """ Cycles the DemoProcess' current temperature attribute
        between high and low limits.
        """
        self.current_temperature += self._temperature_delta
        if (self.current_temperature >= self.max_temperature or
            self.current_temperature <= self.min_temperature):
            self._temperature_delta *= -1

    def _update_percent(self):
        """ Cycles the DemoProcess' current floating point 
        percent attribute between high and low limits.
        """
        self.current_percent += self._percent_delta
        if (self.current_percent >= self.max_percent or
            self.current_percent <= self.min_percent):
            self._percent_delta *= -1

    def _update_state(self):
        """ Randomly changes the DemoProcess' current_state_name
        attribute to one of its allowed enum name values.
        """
        self._state_count -= 1
        if self._state_count <= 0:
            self._state_count = self._state_delay
            state_list = list(DemoStates)
            self.current_state_name = random.choice(state_list).name

    def _init_demo_color(self, demo_ui):
        """ Sets up the demonstration of color attributes """
        self.max_color_value = 999
        self.min_color_value = 0
        self.demo_red_value = 500
        self.demo_green_value = 500
        self.demo_blue_value = 500
        self.demo_red_delta = 3
        self.demo_green_delta = 6
        self.demo_blue_delta = 9

        self.demo_color_pair2 = 1
        self.demo_pair2_delta = 1

        self.demo_color_number = demo_ui.total_color_numbers - 1
        self._set_demo_color(self.demo_red_value,
                            self.demo_green_value,
                            self.demo_blue_value)

        self.total_color_pairs = demo_ui.total_color_pairs
        self.demo_color_pair = self.total_color_pairs - 1

        curses.init_pair(self.demo_color_pair,
                         curses.COLOR_BLACK,
                         self.demo_color_number)

    def _set_demo_color(self, red, green, blue):
        """ Assigns a new RGB color value to the color number 
        used by the color demonstration.
        """
        # (TODO: throws an exception with simpler displays e.g. TERM=xterm)
        curses.init_color(self.demo_color_number,
                          min(self.max_color_value,
                              max(red, self.min_color_value)),
                          min(self.max_color_value,
                              max(green, self.min_color_value)),
                          min(self.max_color_value,
                              max(blue, self.min_color_value)))

    def _update_color(self):
        """ Cycles the demo color number through its range of
        allowed values.
        """
        self.demo_red_value += self.demo_red_delta
        if (self.demo_red_value >= self.max_color_value or
            self.demo_red_value <= self.min_color_value):
            self.demo_red_delta *= -1

        self.demo_green_value += self.demo_green_delta
        if (self.demo_green_value >= self.max_color_value or
            self.demo_green_value <= self.min_color_value):
            self.demo_green_delta *= -1

        self.demo_blue_value += self.demo_blue_delta
        if (self.demo_blue_value >= self.max_color_value or
            self.demo_blue_value <= self.min_color_value):
            self.demo_blue_delta *= -1

        self._set_demo_color(self.demo_red_value,
                            self.demo_green_value,
                            self.demo_blue_value)

        """
        # Only for testing color pair cycling
        self.demo_color_pair2 += self.demo_pair2_delta
        if (self.demo_color_pair2 >= 255 or
            self.demo_color_pair2 <= 1):
            self.demo_pair2_delta *= -1

        curses.init_pair(self.demo_color_pair2,
                         curses.COLOR_BLACK,
                         self.demo_color_pair2)

        attr = self.colorfield.get_attrs()
        self.colorfield.remove_attrs(attr)
        self.colorfield.add_attrs(curses.color_pair(self.demo_color_pair2))
        """

    def get_demo_color_text(self):
        # return "Color Range {0}".format(self.demo_color_pair2)
        return "Color: R:{0} G:{1} B:{2}".format(
                self.demo_red_value,
                self.demo_green_value,
                self.demo_blue_value)

    def get_demo_temperature_text(self):
        """ Returns a string that displays current temperature """
        return "Current Temp: {0}".format(self.current_temperature)

    def get_demo_percent_text(self):
        """ Returns a string that displays current (floating point) percent value """
        return "Percent: {:.2f}".format(self.current_percent)

    def get_demo_state_text(self):
        """ Returns a string that displays the current state value """
        return "Current State: {0}".format(self.current_state_name)

    def get_demo_mode_text(self):
        """ Returns a string that displays the current mode name """
        mode_list = list(DemoModes)
        return "Current Mode: {0}".format(self.mode.name)

    def get_demo_mode_value(self):
        """ Returns the current mode integer value """
        return self.mode.value

    def set_demo_mode(self, newmode: DemoModes):
        """ Sets the demo's mode attribute. The new 
        mode value must be a DemoMode enum.
        """
        self.mode = newmode

    def get_demo_tmax_text(self):
        """ Returns a string that displays the max temperature value """
        return "Max Temperature: {0}".format(self.max_temperature)

    def set_demo_max_temperature(self, tmax):
        """ Sets the max temperature limit """
        self.max_temperature = tmax

    def get_demo_tmin_text(self):
        """ Returns a string that displays the min temperature value """
        return "Min Temperature: {0}".format(self.min_temperature)

    def set_demo_min_temperature(self, tmin):
        """ Sets the min temperature limit """
        self.min_temperature = tmin

    def get_demo_pmax_text(self):
        """ Returns a string that displays the max percent value """
        return "Max Percent: {0}".format(self.max_percent)

    def set_demo_max_percent(self, pmax):
        """ Sets the max percent limit """
        self.max_percent = pmax

    def get_demo_pmin_text(self):
        """ Returns a string that displays the min percent value """
        return "Min Percent: {0}".format(self.min_percent)

    def set_demo_min_percent(self, pmin):
        """ Sets the min percent limit """
        self.min_percent = pmin

    async def run_fast(self):
        """ Runs a demonstration process coroutine concurrently
        with other processes.  To run concurrently this method
        must be declared with an "async" prefix and called with
        an "await" prefix. It also needs to include a periodic
        call to a yield routine such as asyncio.sleep(). The
        argument to sleep() can be 0 if you want to yield for
        the shortest time possible.
        """
        while True:
            self._update_color()
            self._update_percent()
            #await asyncio.sleep(.02)
            await asyncio.sleep(1)

    async def run_slow(self):
        """ Runs a second demonstration process coroutine
        concurrently with other processes.  
        """
        while True:
            self._update_temperature()
            self._update_state()
            self._update_color()
            await asyncio.sleep(2)

    def setup_demo_display(self, demo_ui):
        """ Defines all the Windows for this demonstration UI. 

        Note that you need to declare this setup method to have
        two arguments; the first is the typical "self" argument
        argument that every class method gets, and the second 
        will be a reference to your CursesUI instance. You will
        need both because this setup routine essentially becomes
        a bridge between this process instance and the CursesUI
        instance.

        This example method will install default Windows for the 
        CursesUI demo. Use it as an example for creating the user
        interface for your own application.
        """
        # Create a SubWindow instance for menu messages
        menuwin = SubWindow(demo_ui.display, 10, 30, 2, 2, "Menu")

        # Add some static menu items to the menu Window.
        #
        # These never change so they do not need update
        # callback functions. Note that you can also
        # use a single Textfield to display multiple
        # lines of text. Any empty, trailing newlines
        # will be stripped from your text.
        menurow = menuwin.get_first_row()
        menucol = menuwin.get_center_col()
        menu1 = ("Press <Tab> to select next\n"
                 "<Enter> to go in selected\n"
                 "<Esc> to go back out\n"
                 "Ctrl-p adds a message\n"
                 "Arrows scroll messages\n"
                 "Resize at will\n"
                 "Ctrl-x to exit")
        menu1field = Textfield(menurow, menucol, Align.CENTER)
        menu1field.write(menu1)
        menuwin.add_field(menu1field)

        # The menu Window is read-only so make it unselectable
        menuwin.set_selectable(False)

        # Create a SubWindow for current status. Position it
        # relative to the menu Window.
        row = menuwin.get_top_edge_row()
        col = menuwin.get_right_edge_col() + 2
        stswin = SubWindow(demo_ui.display, 10, 30, row, col, "Status")

        # Add current time to the Status Window.
        row = stswin.get_first_row()
        col = stswin.get_center_col()
        timefield = Textfield(row, col, Align.CENTER)

        # Since the time is always changing, we need
        # an update callback function to refresh the
        # time Textfield.
        def _get_current_time_text():
            return "{0}".format(
                time.asctime(time.localtime(time.time())))

        # Add the update callback to the Textfield.
        timefield.set_update_cb(_get_current_time_text)

        # Finally, add the time Textfield to the status
        # Window.
        stswin.add_field(timefield)

        # Add the demo process current temperature to the status
        # Window, leaving a blank line between this Textfield and
        # the time Textfield above.
        #
        # Note that before you call get_required_rows() you may need
        # to call the Textfield's update() method to populate the
        # Textfield with the actual text. If you don't and the
        # Textfield's content is empty then get_required_rows() will
        # return 0.
        timefield.update()
        row += timefield.get_required_rows()
        row += 1
        col = stswin.get_first_col()
        tempfield = Textfield(row, col)
        tempfield.set_update_cb(self.get_demo_temperature_text)
        stswin.add_field(tempfield)

        # Populate the Textfield before asking for the required
        # rows.
        tempfield.update()
        row += tempfield.get_required_rows()

        # Add current demo process state value to the status window.
        statefield = Textfield(row, col)
        statefield.set_update_cb(self.get_demo_state_text)
        stswin.add_field(statefield)
        statefield.update()
        row += statefield.get_required_rows()

        # Uncomment the following line to test Textfield attributes.
        # These attributes will apply to the Textfield content only.
        # statefield.add_attrs(curses.A_BOLD)

        # Add current demo process color test to the status window.
        self._init_demo_color(demo_ui)
        colorfield = Textfield(row, col)
        colorfield.set_update_cb(self.get_demo_color_text)
        stswin.add_field(colorfield)
        colorfield.add_attrs(curses.color_pair(self.demo_color_pair))
        colorfield.update()
        row += colorfield.get_required_rows()

        # Only for testing color pair cycling
        self.colorfield = colorfield

        # Add the percent field (for testing floating point values)
        percentfield = Textfield(row, col)
        percentfield.set_update_cb(self.get_demo_percent_text)
        stswin.add_field(percentfield)

        # Populate the Textfield before asking for the required
        # rows.
        percentfield.update()
        row += percentfield.get_required_rows()

        # Uncomment these lines as you like for testing. These will
        # apply to the entire status Window:
        # stswin.add_attrs(curses.A_REVERSE)
        # stswin.hide_border()
        # stswin.select()

        # Create a SubWindow for values that the user can control. 
        # Position it relative to the menu and status Windows.
        row = menuwin.get_top_edge_row()
        col = stswin.get_right_edge_col() + 2
        ctlwin = SubWindow(demo_ui.display, 10, 30, row, col, "Controls")

        # Add max & min temperature limits to the controls Window.
        row = ctlwin.get_first_row()
        col = ctlwin.get_first_col()
        tmaxfield = Textfield(row, col)
        tmaxfield.set_update_cb(self.get_demo_tmax_text)
        ctlwin.add_field(tmaxfield)
        tmaxfield.update()
        row += tmaxfield.get_required_rows()

        tminfield = Textfield(row, col)
        tminfield.set_update_cb(self.get_demo_tmin_text)
        ctlwin.add_field(tminfield)
        tminfield.update()
        row += tminfield.get_required_rows()

        # Add the current mode enum Textfield to the controls Window.
        modefield = Textfield(row, col)
        modefield.set_update_cb(self.get_demo_mode_text)
        ctlwin.add_field(modefield)
        modefield.update()
        row += modefield.get_required_rows()

        # Add max & min percent limits to the controls Window. These
        # are for testing the display and editing of floating point values.
        pmaxfield = Textfield(row, col)
        pmaxfield.set_update_cb(self.get_demo_pmax_text)
        ctlwin.add_field(pmaxfield)
        pmaxfield.update()
        row += pmaxfield.get_required_rows()

        pminfield = Textfield(row, col)
        pminfield.set_update_cb(self.get_demo_pmin_text)
        ctlwin.add_field(pminfield)
        pminfield.update()
        row += pminfield.get_required_rows()

        # Add dialog instances to these Textfields to make them
        # editable. You need to provide each dialog instance with
        # callback routine that will write the new value into the
        # variable that the Textfield displays.
        #
        # The first two of these EditDialogs get integer values from
        # the user. If needed you can configure an EditDialog instance
        # to instead return float values or even just the raw text.
        maxdialog = EditDialog(demo_ui.display, 
                               "Enter the new maximum\n"
                               "temperature:",
                               self.set_demo_max_temperature)
        tmaxfield.set_dialog(maxdialog)

        mindialog = EditDialog(demo_ui.display, 
                               "Enter the new mimimum\n"
                               "temperature:",
                               self.set_demo_min_temperature)
        tminfield.set_dialog(mindialog)

        # This EnumDialog instance allows the user to pick an enum
        # constant from a list of all possible members of (in this
        # case) the DemoModes enum.
        modedialog = EnumDialog(demo_ui.display, DemoModes,
                               "Select the new mode: ",
                               self.set_demo_mode)
        modefield.set_dialog(modedialog)

        # These allow the user to change the demo process floating
        # point min and max percentage values.
        pmaxdialog = FloatDialog(demo_ui.display, 
                                "Enter the new maximum\n"
                                "percentage:",
                                self.set_demo_max_percent)
        pmaxfield.set_dialog(pmaxdialog)

        pmindialog = FloatDialog(demo_ui.display, 
                                "Enter the new mimimum\n"
                                "percentage:",
                                self.set_demo_min_percent)
        pminfield.set_dialog(pmindialog)

        # Create a PadWindow at the bottom for status messages.
        #
        # For PadWindows the width and height apply to the underlying
        # pad dimensions, which can be any size at all. Subtracting 2
        # here just accounts for the width of the right and left
        # borders, so that this pad should be fully visible in the
        # PadWindow's bordered viewport without needing to scroll
        # horizontally.
        width = demo_ui.display.get_last_col() - 2

        # We'll choose to make the height of the pad equal to the
        # size of the TextBuffer that holds output sent to stdout
        # and stderr during the CursesUI session.
        height = demo_ui.stdout_bfr.get_maxlines()

        # Specify upper-left and lower-right corners of the viewport.
        # These make the Messages Window fill the entire bottom 
        # section of the display Window at whatever its current size
        # is when the CursesUI instance starts.
        ulcrow = menuwin.get_bottom_edge_row() + 1
        ulccol = 1
        lrcrow = demo_ui.display.get_last_row()
        lrccol = demo_ui.display.get_last_col()

        def _get_demo_stdout_text():
            # A local update callback that displays in the Messages
            # Window any log messages and any output from calls to
            # print().
            return demo_ui.stdout_bfr.read()

        # Create the Messages PadWindow
        msgwin = PadWindow(demo_ui.display, height, width, ulcrow,
                           ulccol, lrcrow, lrccol, "Messages")

        # Add a single Textfield that will display all message
        # lines in the stdout_bfr. Locate this Textfield at the
        # upper leftmost corner of the pad.
        msgfield = Textfield(0, 0)
        msgfield.set_update_cb(_get_demo_stdout_text)
        msgwin.add_field(msgfield)

        # Uncomment this if you like to test attributes that
        # will apply to the entire Window and its contents:
        # msgwin.add_attrs(curses.A_REVERSE)

        # Create the KeyResponse instance for arrow keys.
        # These keys will scroll the contents of the Messages
        # Window.
        arrow_key_list = [curses.KEY_UP, curses.KEY_DOWN,
                          curses.KEY_RIGHT, curses.KEY_LEFT]
        arrow_keys = KeyResponse("arrows", arrow_key_list)

        # If we add this KeyResponse to the msgwin, then the 
        # arrow keys will only be active while the msgwin is
        # selected.  If instead we add the KeyResponse instance
        # to the display Window, then the arrow keys will be
        # active during the entire CursesUI session. You can
        # test this by switching the comment character between
        # the two statements below.
        #
        # msgwin.add_key(arrow_keys)
        demo_ui.display.add_key(arrow_keys)

        def _kr_scroll_msgwin(keyhit):
            # This is a single local key response routine that
            # handles scrolling the Messages Window in any of
            # the 4 directions.

            if keyhit == curses.KEY_UP:
                msgwin.scroll_up()
            elif keyhit == curses.KEY_DOWN:
                msgwin.scroll_down()
            elif keyhit == curses.KEY_RIGHT:
                msgwin.scroll_right()
            elif keyhit == curses.KEY_LEFT:
                msgwin.scroll_left()

        # Bind the scrolling key response routine to the
        # arrow keys.
        arrow_keys.bind(_kr_scroll_msgwin)

    def setup_demo_responses(self, demo_ui):
        """ Configure the initial key responses for the demo UI.

        Note that you need to declare this setup method to have
        two arguments; the first is the typical "self" argument
        that every class method gets, and the second will be a
        reference to your CursesUI instance. You may need both
        because this setup routine essentially becomes a bridge
        between this process instance and the CursesUI instance.

        This is where you might typically set up key responses
        that will be active during the entire UI session. To do
        so you would add the KeyResponse instances to the top
        level Display Window instance (which is always present).

        Other Window instances can have their own key responses
        to react to specific user keyhits. If you add KeyResponse
        instances to a specific Window instance, then those 
        responses will only be active when that particular Window
        is selected.

        This example method will install default key responses 
        for the CursesUI demo. Use it as an example for creating
        the user interface for your own application.
        """
        # Note that curses.ascii.ctrl('x') returns the same
        # type you pass to it; given 'x' it returns string
        # '\x18', not the integer value 0x18. 
        #
        # ord() converts a character to its integer value.
        #
        # So to get the integer value we need to use ord()
        # on either the argument or on the return value. Either
        # way will work.
        #
        # Create a KeyResponse instance for Ctrl-x and
        # add it to the display Window.
        ctrl_x_key = KeyResponse("ctrl_x", ord(curses.ascii.ctrl('x')))
        demo_ui.display.add_key(ctrl_x_key)
        ctrl_x_key.bind(demo_ui.kr_done_with_ui)

        # Create and install the KeyResponse instance for Ctrl-p
        ctrl_p_key = KeyResponse("ctrl_p", ord(curses.ascii.ctrl('p')))
        demo_ui.display.add_key(ctrl_p_key)

        def _kr_ctrl_p_response(_):
            # Define some random message strings to print
            msglist = [
                "Hello, world.",
                "Forty-two.",
                "Beautiful is better than ugly.",
                "Readability counts.",
                "Nobody expects the Spanish Inquisition!",
                "What is the air-speed velocity of an unladen swallow?",
                "So long and thanks for all the fish.",
                "Don't panic.",
                "THIS IS AN EX-PARROT!!",
                ]

            # Note that while the CursesUI instance has control of the
            # screen, you can still use simple print statements even
            # though curses is maintaining its windows.  Output from
            # print() statements will go instead into the stdout_bfr
            # which will be dumped to the screen on exit. 
            #
            # Also, the demo's Message Window displays the contents
            # of the stdout_bfr. So for the demo, any print() output
            # will be visible there too.
            print("Msg: {0}".format(random.choice(msglist)))
            # print(globals()['log'])

        # Bind Ctrl-p to its local response routine
        ctrl_p_key.bind(_kr_ctrl_p_response)

        # Create and install the KeyResponse instance for TAB
        tab_key = KeyResponse("tab", curses.ascii.TAB)
        demo_ui.display.add_key(tab_key)

        # The TAB key will select the next child Window
        tab_key.bind(demo_ui.display.kr_select_next_child)

        # Create and install the KeyResponse instance for ENTER
        enter_key = KeyResponse("enter", curses.ascii.LF)
        demo_ui.display.add_key(enter_key)

        # ENTER will begin editing the selected child Window
        enter_key.bind(demo_ui.display.kr_begin_child_edit)

#
# The code below runs only when demoprocess.py is invoked from the
# command line with "python3 demoprocess.py"
# 
if __name__ == "__main__":

    # The normal curses keyboard handling system adds a 
    # configurable delay to the ESCAPE key so that it can
    # be combined with other keys to generate special keycodes.
    # The delay is typically around 1 second, which can be
    # noticably slow if you are not using the ESCAPE key that way.
    # You can change the delay by setting the ESCDELAY environment
    # variable to a shorter delay but you have to change it before
    # the curses windowing system gets initialized.
    #
    # Since the demoUI system does use the ESCAPE key we will set
    # a shorter delay (in milliseconds) here. 
    import os
    os.environ.setdefault('ESCDELAY', '25')

    import logging

    # Set up a CursesUI instance to run concurrently with the 
    # DemoProcess instance.
    from cursesui import (CursesUI, log, Align, Textfield, KeyResponse,
                          SubWindow, NewWindow, PadWindow, EditDialog,
                          FloatDialog, EnumDialog, ListDialog, TextDialog)
    demo_process = DemoProcess()

    # Create the demonstration user interface, telling it how
    # to set up the display and keyboard responses.
    demoUI = CursesUI(demo_process.setup_demo_display, 
                      demo_process.setup_demo_responses,
                      "CursesUI Full Demo")

    # Alternatively you could install the display and key response
    # setup routines after creating the CursesUI instance, like
    # so:
    #
    # demoUI = CursesUI()
    # demoUI.set_display_builder(demo_process.setup_demo_display)
    # demoUI.set_response_builder(demo_process.setup_demo_responses)
    # demoUI.add_title("CursesUI Full Demo")

    # Tell the user interface to run the demo processes concurrently.
    demoUI.add_coroutine(demo_process.run_fast)    
    demoUI.add_coroutine(demo_process.run_slow)    

    # Set up the logging level for this demonstration.
    #
    # Typical log filter levels are logging.DEBUG 
    # for development, logging.ERROR for normal use.
    # Set level to logging.CRITICAL + 1 to suppress
    # all log messages from a CursesUI instance.
    #
    # demoUI.initialize_loglevel(logging.DEBUG)
    demoUI.initialize_loglevel(logging.WARNING)

    # Run the CursesUI instance until the user quits
    demoUI.run()
