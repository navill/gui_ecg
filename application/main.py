import threading
from collections import deque

from gui.gui_handler import GUIDrawer
from serial_handler.async_timer import UARTReceiver
from serial_handler.port_handler import get_valid_comport


class MainProcessor:
    def __init__(self):
        self.queue = deque([0 for _ in range(1000)], maxlen=1000)
        self.uart_handler = None
        self.gui_handler = None

    def initialize(self):
        self.initialize_uart()
        self.initialize_gui()

    def initialize_uart(self, timeout=3, port=None):
        if port is None:
            port = get_valid_comport()
        self.uart_handler = UARTReceiver(timeout=timeout, port=port, queue=self.queue)

    def initialize_gui(self):
        self.gui_handler = GUIDrawer(queue=self.queue)

    def start_thread(self):
        thread = threading.Thread(target=self.uart_handler.get_data, daemon=True)
        thread.start()

    def draw_graph(self):
        self.initialize()
        self.start_thread()
        self.gui_handler.do_process()


if __name__ == '__main__':
    main = MainProcessor()
    main.draw_graph()
