import threading
import tkinter
from collections import deque
from tkinter import *

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from serial_handler.async_timer import UARTReceiver
from serial_handler.port_handler import get_valid_comport

FONT = ("Arial Bold", 20)
button_width = 6
button_padx = "2m"
button_pady = "1m"
buttons_frame_padx = "3m"
buttons_frame_pady = "2m"
buttons_frame_ipadx = "3m"
buttons_frame_ipady = "1m"


class GUIInterface(tkinter.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # container
        self.container_frame = Frame(self, background='grey')
        self.container_frame.pack()

        self.empty_top_frame = Frame(self.container_frame, height=20)
        self.empty_top_frame.pack(side='top', fill='both', expand=True)

        self.draw_frame = Frame(self.container_frame, background='white')
        self.draw_frame.pack(side='left', fill='both', expand=True)

        self.utility_frame = Frame(self.container_frame, borderwidth=5, relief='ridge', height=25)
        self.utility_frame.pack(side='right', fill='y', expand=True)

        self.utility_left_frame = Frame(self.utility_frame)
        self.utility_left_frame.pack(side='left', fill='y', expand=True, padx=5)

        self.utility_right_frame = Frame(self.utility_frame)
        self.utility_right_frame.pack(side='right', fill='y', expand=True, padx=5)

        self.utility_bottom_frame = Frame(self.utility_frame)
        self.utility_bottom_frame.pack(side='bottom', fill='x', expand=True, padx=5, pady=5)

    def set_window(self):
        self.title('ECG MONITOR')
        self.geometry('1000x1050')

    # def set_frame(self):
    # self.draw_frame = Frame(self)
    # self.draw_frame.grid(column=0, row=0, sticky='N W E S')
    # self.draw_frame.pack(side='left', fill='both', expand=True)
    #
    # self.utility_frame = Frame(self)
    # self.utility_frame.grid(column=1, row=0, sticky='N W E S')
    # self.utility_frame.pack(side='right', fill='both', expand=True)
    # self.columnconfigure(0, weight=1)
    # self.rowconfigure(0, weight=1)

    # def set_label(self):
    #     self.label = ttk.Label(self.mainframe, text='ECG monitor', font=FONT)
    #     self.label.grid(column=0, row=0)
    #     self.label.pack(side='top')

    def initialize_interface(self):
        self.set_window()
        # self.set_frame()
        # self.set_label()


class GUIDrawer(GUIInterface):
    def __init__(self, sec: int = 2, scale: float = 0.002, queue=None, **kwargs):
        super().__init__(**kwargs)
        self.x = np.arange(0, 2, scale)
        self.fig, (self.origin, self.filtered) = plt.subplots(2, 1)
        self.origin_graph, = self.origin.plot(self.x, queue, animated=True, lw=2)
        self.filtered_graph, = self.filtered.plot(self.x, queue, animated=True, lw=2)
        self.origin.set_ylim(0.0, 4.0)
        self.filtered.set_ylim(0.0, 4.0)

        self.sec = sec
        self.scale = scale
        self.queue = queue

    def set_time(self, sec=None, scale=None):
        if sec and scale:
            self.x = np.arange(0, sec, sec / self.scale)

    def add_exit_button(self):
        button = Button(master=self.utility_right_frame, text="Quit", overrelief="solid", width=10, height=10,
                        command=self.quit)
        button.configure(background='grey')
        button.pack(side='right', expand=True)

    def add_pause_button(self):
        button = Button(master=self.utility_left_frame, text="Pause")
        button.configure(background='green')
        button.pack(side='right')

    def draw_canvas(self):
        canvas = FigureCanvasTkAgg(self.fig, master=self.draw_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(column=0, row=0)
        canvas_widget.pack(side=tkinter.TOP, expand=True)

    def animate(self, data=None):
        self.origin_graph.set_ydata(list(self.queue))
        self.filtered_graph.set_ydata(list(self.queue))
        return [self.origin_graph, self.filtered_graph, ]

    def do_process(self):
        self.initialize_interface()
        self.set_time()
        self.draw_canvas()
        self.add_exit_button()
        self.add_pause_button()

        _ = animation.FuncAnimation(fig=self.fig, func=self.animate, blit=True, interval=50, save_count=50)
        self.mainloop()


if __name__ == '__main__':
    q = deque([0 for _ in range(1000)], maxlen=1000)
    comport = get_valid_comport()

    uart_receiver = UARTReceiver(timeout=3, port=comport, queue=q)
    gui_drawer = GUIDrawer(queue=q)

    t = threading.Thread(target=uart_receiver.get_data, daemon=True)
    t.start()
    gui_drawer.do_process()
