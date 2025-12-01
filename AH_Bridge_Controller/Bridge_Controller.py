"""Aims of this program:
        - Communicate with bridge.
        - Creates a live graph from bridge.
    Based on https://pythonprogramming.net/live-graphs-matplotlib-tutorial/
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
import pandas as pd
import numpy as np
import pyvisa
import time
from threading import Thread, Event
import re
import tkinter.messagebox as msg_box


class ControllerUI:
    def __init__(self, fig):
        self._fig = fig
        self._ax = fig.subplots()
        fig.subplots_adjust(bottom=0.4)

        self._fn = ""
        self._inst = ""
        self._rec_t = 0
        self._dis_t = 1000

        self._animating = False

        self.setup_textboxes()

        self.setup_buttons()

        self._ani = animation.FuncAnimation(fig, self.animate, interval=1000)

    def setup_textboxes(self):
        #4 lines below denote the space where each textbox lives
        ax_fn = self._fig.add_axes([0.13, 0.27, 0.3, 0.05])
        ax_inst = self._fig.add_axes([0.63, 0.27, 0.3, 0.05])
        ax_rec_t = self._fig.add_axes([0.13, 0.17, 0.3, 0.05])
        ax_dis_t = self._fig.add_axes([0.63, 0.17, 0.3, 0.05])

        self._fn_tb = TextBox(ax_fn, "Filename", textalignment="center") #textbox containing filename for data 
        self._inst_tb = TextBox(ax_inst, "Instrument Address", textalignment="center") #textbox containing instrument port address
        self._rec_t_tb = TextBox(ax_rec_t, "Record Interval [ms]", textalignment="center") #textbox containing time interval between samples 
        self._dis_t_tb = TextBox(ax_dis_t, "Display Interval [ms]", textalignment="center") #textbox containing display refresh time

        self._fn_tb.on_submit(self.change_fn) #Trigger functions when textboxes are filled.
        self._inst_tb.on_submit(self.change_inst)
        self._rec_t_tb.on_submit(self.change_rec_t)
        self._dis_t_tb.on_submit(self.change_dis_t)

    def setup_buttons(self):
        #4 lines below denote the space where each button lives
        ax_rec = self._fig.add_axes([0.5, 0.05, 0.1, 0.075])
        ax_pau = self._fig.add_axes([0.61, 0.05, 0.1, 0.075])
        ax_sav = self._fig.add_axes([0.72, 0.05, 0.1, 0.075])
        ax_res = self._fig.add_axes([0.83, 0.05, 0.1, 0.075])

        self._rec_but = Button(ax_rec, "Record") #Record data button
        self._pau_but = Button(ax_pau, "Pause") #Pause button
        self._sav_but = Button(ax_sav, "Save") #Save button
        self._res_but = Button(ax_res, "Reset") #Reset button

        self._rec_but.on_clicked(self.record)
        self._pau_but.on_clicked(self.pause)
        self._sav_but.on_clicked(self.save)
        self._res_but.on_clicked(self.reset)

    def change_fn(self, expression):
        self._fn = expression

    def change_inst(self, expression):
        self._inst = expression

    def change_rec_t(self, expression):
        t = 0
        try:
            t = int(expression)
        except:
            print("USER did not enter integer for rec_t.")
            t = self._rec_t
            self._rec_t_tb.set_val(t) #I hope this won't call some nightmarish infinite recursion.
        self._rec_t = t

    def change_dis_t(self, expression):
        t = 0
        try:
            t = int(expression)
        except:
            print("USER did not enter integer for dis_t.")
            t = self._dis_t
            self._dis_t_tb.set_val(t)
        self._dis_t = t
        

    def save(self, event):
        if self._animating:
            self._ani.event_source.stop()

        if re.fullmatch(r"\w+\.csv", self._fn) is None:
            self.popup("FILENAME ERROR", f"{self._fn} is not a .csv file!")
        else:
            pass

        if self._animating:
            self._ani.event_source.start()
        
    def popup(self, title, msg):
        popup = msg_box.showerror(title, msg)

    def reset(self, event):
        pass

    def record(self, event):
        self._ani.event_source.start()
        self._animating = True

    def pause(self, event):
        self._ani.event_source.stop()
        self._animating = False
    
    def animate(self, i):
        plt.draw()

class DataRecorder:
    def __init__(self):
        self._fn = ""
        self._inst = ""
        self._rec_t = 0 

        self._rec = False

    def update(self):
        pass

    def record(self):
        pass


if __name__ == "__main__":
    style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure()
    ui = ControllerUI(fig)
    plt.show()