import datetime
import logging
import sys

from serial import Serial

logging.getLogger("asyncio").setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',
                    filename=f'../application/logs/UART_{datetime.date.today()}.log',
                    level=logging.DEBUG)


class UARTReceiver:
    def __init__(self, timeout: int = 0, port: str = 'COM3', baud_rate: int = 921600,
                 queue=None, loop=None):
        self.timeout = timeout
        self.port = port
        self.baud_rate = baud_rate
        self.queue = queue
        try:
            self.serial_port = self.initialize_serial()
            logging.info('Initialized')
        except Exception as e:
            logging.error(f"UART Initialization Error: {e}")
            sys.exit()

    def initialize_serial(self) -> Serial:
        serial_object = Serial(port=self.port, baudrate=self.baud_rate)
        logging.info(f'Set Port: {self.port}')
        return serial_object

    def get_data(self):
        while True:
            try:
                data = self.serial_port.readline()
                self.queue.append(int(data) / 1000)
            except Exception as e:
                print(e)
                raise

#
# if __name__ == '__main__':
#     q = deque([0 for _ in range(100)], maxlen=100)
#     port = get_valid_comport()
#     uart = UARTReceiver(timeout=3, port=port, queue=q)
#     t = threading.Thread(target=uart.get_data)
#     # t.daemon = True
#     t.start()
