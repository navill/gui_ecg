import threading
import tkinter
from tkinter import *
from tkinter import ttk
from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from serial_handler.async_timer import UARTReceiver
from serial_handler.port_handler import get_valid_comport

FONT = ("Arial Bold", 20)


class GUIInterface(tkinter.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = None
        self.mainframe = None

    def set_frame(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.axe.set_ylim(0, 4.0)
        self.axe.grid()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def set_label(self):
        self.label = ttk.Label(self.mainframe, text='ECG monitor', font=FONT, bg='white')
        self.label.grid(column=0, row=0)
        self.label.pack(side='top')

    def initialize_interface(self):
        self.title('ecg')
        self.set_frame()
        self.set_label()


class GUIDrawer(GUIInterface):
    def __init__(self, sec: int = 2, scale: float = 0.002, queue=None, **kwargs):
        super().__init__(**kwargs)
        self.fig = plt.Figure()
        self.axe = self.fig.add_subplot()
        self.x = np.arange(0, 2, scale)
        self.line, = self.axe.plot(self.x, queue, lw=2)
        self.sec = sec
        self.scale = scale
        self.queue = queue

    def set_time(self, sec=None, scale=None):
        if sec and scale:
            self.x = np.arange(0, sec, sec / self.scale)

    def draw_canvas(self):
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().grid(column=0, row=1)

    def animate(self, data=None):
        self.line.set_ydata(list(self.queue))
        return self.line,

    def do_process(self):
        self.initialize_interface()
        self.set_time()
        self.draw_canvas()
        self.animate()
        _ = animation.FuncAnimation(fig=self.fig, func=self.animate, interval=50, save_count=50)
        self.mainloop()


if __name__ == '__main__':
    q = deque([0 for _ in range(1000)], maxlen=1000)
    comport = get_valid_comport()

    uart_receiver = UARTReceiver(timeout=3, port=comport, queue=q)
    gui_drawer = GUIDrawer(queue=q)

    t = threading.Thread(target=uart_receiver.get_data, daemon=True)
    t.start()
    gui_drawer.do_process()
