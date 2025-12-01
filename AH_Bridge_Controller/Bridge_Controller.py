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

class ControllerUI:
    def __init__(self, fig):
        self._fig = fig
        self._ax = fig.subplots()
        fig.subplots_adjust(bottom=0.4)

        self._fn = ""
        self._inst = ""

        ax_fn = fig.add_axes([0.13, 0.27, 0.3, 0.05])
        ax_inst = fig.add_axes([0.63, 0.27, 0.3, 0.05])
        ax_rec_t = fig.add_axes([0.13, 0.17, 0.3, 0.05])
        ax_dis_t = fig.add_axes([0.63, 0.17, 0.3, 0.05])

        ax_rec = fig.add_axes([0.5, 0.05, 0.1, 0.075])
        ax_pau = fig.add_axes([0.61, 0.05, 0.1, 0.075])
        ax_sav = fig.add_axes([0.72, 0.05, 0.1, 0.075])
        ax_res = fig.add_axes([0.83, 0.05, 0.1, 0.075])

        self._fn_tb = TextBox(ax_fn, "Filename", textalignment="center") #textbox containing filename for data 
        self._inst_tb = TextBox(ax_inst, "Instrument Address", textalignment="center") #textbox containing instrument port address
        self._rec_t_tb = TextBox(ax_rec_t, "Record Interval [ms]", textalignment="center") #textbox containing instrument port address
        self._dis_t_tb = TextBox(ax_dis_t, "Display Interval [ms]", textalignment="center") #textbox containing instrument port address

        self._fn_tb.on_submit(self.change_fn) #Trigger functions when textboxes are filled.
        self._inst_tb.on_submit(self.change_inst)
        self._rec_t_tb.on_submit(self.change_rec_t)
        self._dis_t_tb.on_submit(self.change_dis_t)

        self._rec_but = Button(ax_rec, "Record") #Record data button
        self._pau_but = Button(ax_pau, "Pause") #Pause button
        self._sav_but = Button(ax_sav, "Save") #Pause button
        self._res_but = Button(ax_res, "Reset") #Pause button

        self._rec_but.on_clicked(self.record)
        self._pau_but.on_clicked(self.pause)
        self._sav_but.on_clicked(self.save)
        self._res_but.on_clicked(self.reset)

        self._ani = animation.FuncAnimation(fig, self.animate, interval=1000)

    def change_fn(self, expression):
        self._fn = expression

    def change_inst(self, expression):
        self._inst = expression

    def change_rec_t(self, expression):
        pass

    def change_dis_t(self, expression):
        pass

    def save(self, event):
        pass

    def reset(self, event):
        pass

    def record(self, event):
        self._ani.event_source.start()

    def pause(self, event):
        self._ani.event_source.stop()
    
    def animate(self, i):
        plt.draw()


style.use("seaborn-v0_8-whitegrid")

fig = plt.figure()

ui = ControllerUI(fig)
plt.show()