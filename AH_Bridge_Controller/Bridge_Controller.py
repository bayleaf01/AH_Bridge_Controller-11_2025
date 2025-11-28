"""Aims of this program:
        - Communicate with bridge.
        - Creates a live graph from bridge.
    Based on https://pythonprogramming.net/live-graphs-matplotlib-tutorial/
"""


import pyvisa
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
import pandas as pd
import numpy as np
import os.path

class UI:
    def __init__(self, fig):
        self._fig = fig
        self._ax = fig.subplots()

        ax_fn = fig.add_axes([0.1, 0.05, 0.8, 0.075])
        ax_inst = fig.add_axes([0.2, 0.05, 0.8, 0.075])

        ax_rec = fig.add_axes([0.7, 0.05, 0.1, 0.075])
        ax_pau = fig.add_axes([0.81, 0.05, 0.1, 0.075])

        self._data_rec = DataRecorder()

        self._fn_tb = TextBox(ax_fn, "Filename", textalignment="center") #textbox containing filename for data 
        self._inst_tb = TextBox(ax_inst, "Instrument Address", textalignment="center") #textbox containing instrument port address

        self._fn_tb.on_submit(self.change_fn) #Trigger functions when textboxes are filled.
        self._inst_tb.on_submit(self.change_inst)

        self._rec_but = Button(ax_rec, "Record") #Record data button
        self._pau_but = Button(ax_pau, "Pause") #Pause button

        self._fn = ""
        self._inst = ""

    def change_fn(self, expression):
        self._fn = expression

    def change_inst(self, expression):
        self._inst = expression

    def record(self, event):
        self._data_rec.record()

    def pause(self, event):
        self._data_rec.pause()
    
    def animate(self, i):
        t, C = self._data_rec.get_data()
        
        self._ax.clear()

        self._ax.plot(t, C)

class DataRecorder:
    def __init__(self):
        self._bri_con = BridgeController()
        self._data = {"t[s]": [], "C[pF]": []}
        self._t = []
        self._C = []

        self._temp_fn = "temp_data.csv"

    def get_data(self):
        return self._t, self._C
    
    def save_data(self, fn):
        self._data["t[s]"] = self._t
        self._data["C[s]"] = self._C

        df = pd.DataFrame(data = self._data)

        df.to_csv(fn)

    def record(self, event):
        pass
        
    def pause(self, event):
        pass

class BridgeController:
    pass

style.use("seaborn-v0_8-whitegrid")

fig = plt.figure()

ui = UI(fig)
ani = animation.FuncAnimation(fig, ui.animate, interval=1000)
plt.show()