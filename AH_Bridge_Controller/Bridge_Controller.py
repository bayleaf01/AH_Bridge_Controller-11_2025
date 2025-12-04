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
import random


class ControllerUI:
    def __init__(self, plt, data_event, sf_event, rec_event, res_event, end_event):
        self._plt = plt
        style.use("seaborn-v0_8-whitegrid")
        fig = plt.figure()
        self._fig = fig
        self._ax = fig.subplots()
        fig.subplots_adjust(bottom=0.4)

        self._dr = None

        self._fn = "data.csv"
        self._inst = ""
        self._rec_t = 1
        self._dis_t = 1

        self._lst_dis_t = time.time()

        self._data_event = data_event
        self._sf_event = sf_event
        self._rec_event = rec_event
        self._res_event = res_event
        self._end_event = end_event

        self._animating = False #Is matplot currently animating
        self._is_popup = False #Boolean to stop user producing over one popup.

        self.setup_textboxes()
        self.setup_buttons()

        self._ani = animation.FuncAnimation(fig, self.animate)
        self._ani.event_source.stop()

    def start(self):
        self._plt.show()
        self._end_event.set()

    def animate(self, i):
        time_passed = time.time() - self._lst_dis_t

        if time_passed < self._dis_t:
            return

        if self._data_event.is_set() and self._animating:
            data = self._dr.get_last_dp()
            self._ax.scatter(data[0], data[1], color="r")

        self._lst_dis_t = time.time()


    def setup_textboxes(self):
        #4 lines below denote the space where each textbox lives
        ax_fn = self._fig.add_axes([0.13, 0.27, 0.3, 0.05])
        ax_inst = self._fig.add_axes([0.63, 0.27, 0.3, 0.05])
        ax_rec_t = self._fig.add_axes([0.13, 0.17, 0.3, 0.05])
        #ax_rec_t = self._fig.add_axes([0.4, 0.17, 0.3, 0.05])
        ax_dis_t = self._fig.add_axes([0.63, 0.17, 0.3, 0.05])

        self._fn_tb = TextBox(ax_fn, "Filename", textalignment="center", initial=self._fn) #textbox containing filename for data 
        self._inst_tb = TextBox(ax_inst, "Instrument Address", textalignment="center") #textbox containing instrument port address
        self._rec_t_tb = TextBox(ax_rec_t, "Record Interval [s]", textalignment="center", initial=self._rec_t) #textbox containing time interval between samples 
        self._dis_t_tb = TextBox(ax_dis_t, "Display Interval [s]", textalignment="center", initial=self._dis_t) #textbox containing display refresh time

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
            t = float(expression)
        except:
            print("USER did not enter number for rec_t.")
            t = self._rec_t
            self._rec_t_tb.set_val(t) #I hope this won't call some nightmarish infinite recursion.
        self._rec_t = t

        self._rec_event.set()

    def change_dis_t(self, expression):
        t = 0
        try:
            t = float(expression)
        except:
            print("USER did not enter a number for dis_t.")
            t = self._dis_t
            self._dis_t_tb.set_val(t)

        print(f"Display time {t}s")
        self._dis_t = t
        

    def save(self, event):
        if self._sf_event.is_set():
            return #Stops it doing anything if it is already waiting to do something.
        
        self.pause()

        if re.fullmatch(r"\w+\.csv", self._fn) is None:
            if self._is_popup:
                return
            self._is_popup = True
            self.popup("FILENAME ERROR", f"\"{self._fn}\" is not a .csv file!")
            self._is_popup = False
        else:
            self._sf_event.set()
          
    def popup(self, title, msg):
        msg_box.showerror(title, msg)

    def reset(self, event=None):
        if self._res_event.is_set():
            return #Stops it doing anything if it is already waiting to do something.
        self.pause()
        self._ax.clear()
        self._res_event.set()

    def record(self, event=None):
        #If you type in the record time first and don't click off, clicking on the button counts as two events: submitting the textbox and hitting the button, 
        #so the button function is blocked by the code below.
        #if self._rec_event.is_set(): 
        #    return #Stops it doing anything if it is already waiting to do something.
        #I have commented the code above because I don't think it is needed.
        self._ani.event_source.start()
        self._animating = True
        self._rec_event.set()

    def pause(self, event=None):
        if self._rec_event.is_set():
            return #Stops it doing anything if it is already waiting to do something.

        self._ani.event_source.stop()
        self._animating = False
        self._rec_event.set()

    def get_fn(self):
        return self._fn
    
    def get_rec(self):
        return self._animating
    
    def get_rec_t(self):
        return self._rec_t
    
    def get_inst(self):
        return self._inst
    
    def set_dr(self, dr): #set data recorder
        self._dr = dr

class DataRecorder(Thread):
    def __init__(self, data_event, sf_event, rec_event, res_event, end_event):
        super().__init__()
        self._inst = ""
        self._rec_t = 1 

        self._UI = None

        self._data_event = data_event
        self._sf_event = sf_event
        self._rec_event = rec_event
        self._res_event = res_event
        self._end_event = end_event

        self._strt_t = time.time()
        self._data_shape = (100, 2) #number of data points before auto save on left. Two for the time and cap on right.
        self._autosv_fn = "temp_data.txt"
        self.reset_file()

        self._dp_id = 1
        self._data = np.zeros(shape=self._data_shape) 

        self._rec = False


    def run(self):
        super().run()
        while True:
            time.sleep(self._rec_t) #I think one thread can block the other if there is no sleeping.
            #The sleep is a problem if the time is set too high. It takes time to reset it.
            #For now I will focus on getting it working. If I have time, I should try to sort this out.

            if self._end_event.is_set():
                print("In case I don't see ya, good afternoon, good evening, and good night.")
                return

            if self._sf_event.is_set():
                self.save()
                self._sf_event.clear()

            if self._rec_event.is_set():
                self.record()
                self._rec_event.clear()

            if self._res_event.is_set():
                self.reset()
                self._res_event.clear()

            if self._rec == False:
                continue

            self.measure()
            self._dp_id += 1
            
            if self._dp_id >= self._data_shape[0]:
                self.autosave()

    def measure(self):
        if not self._data_event.is_set():
            self._strt_t = time.time() #Start the timer when you first start recording for the first time.
        self._data[self._dp_id] = [time.time()-self._strt_t, random.random()]
        #print(self._data[self._dp_id])
        self._data_event.set() #Tells the GUI that there are data points to be measured.
    
    def save(self):
        fn = self._UI.get_fn()
        print(f"Saving to {fn}...")
        stored_data = np.genfromtxt(self._autosv_fn)
        complete_data = np.concatenate((stored_data, self._data[1:self._dp_id]), axis=0) #Combines data from the memory with that in temporary storage.
        #print(complete_data[0], complete_data[-1])
        df = pd.DataFrame(data=complete_data, columns=["time [s]", "Cap [pF]"])
        df.to_csv(fn)
        print(f"Done!")

    def autosave(self):
        #if not self._data_event.is_set():
        #    return
        #I will hard code the autosave. It would be better practice to control it through a user input or JSON file.
        with open(self._autosv_fn, "ab") as f:
            np.savetxt(f, self._data[1:]) #appends (not write) data to text file.
            #Does not include the first data point because that was submitted with the last set.
        new_data = np.zeros(shape=self._data_shape)
        new_data[0] = self._data[-1]
        self._data = new_data #clear data to free up space in the memory.
        
        self._dp_id = 1 #The zeroth data point is the last of the previous dataset.

    def reset(self):
        self._data_event.clear()
        self._data = np.zeros(shape=self._data_shape) #clear data
        self._dp_id = 0
        self.reset_file()
        print("Reset")

    def reset_file(self):
        open(self._autosv_fn, "w").close()

    
    def record(self):
        self._rec = self._UI.get_rec()
        self._rec_t = self._UI.get_rec_t()
        self._inst = self._UI.get_inst()

        print(f"Recording is {self._rec} with interval {self._rec_t}s from {self._inst}")


    def set_ui(self, UI): #set ui
        self._UI = UI

    def get_last_dp(self): #gets last data point in sequence
        return self._data[self._dp_id-1] #-1 because the current data point will be undefined. 
        #Data can't be taken until at least one data point exists so i=0 is not worrying.

#class FileSave:
#    def __init__(self, fn, save):
#        self.fn = fn
#        self.save = save

# class Instrument:
#     def __init__(self, name, t, record):
#         self.name = name
#         self.t = t
#         self.record = record

#I need to add temporary and perminant data saving.

if __name__ == "__main__":
    sf_event = Event()
    rec_event = Event()
    res_event = Event()
    end_event = Event()
    data_event = Event()

    ui = ControllerUI(plt, data_event, sf_event, rec_event, res_event, end_event)
    dr = DataRecorder(data_event, sf_event, rec_event, res_event, end_event)

    ui.set_dr(dr)
    dr.set_ui(ui)

    dr.start()
    ui.start() #Figure should be in main thread for whatever reason.

    dr.join()