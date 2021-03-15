import asyncio
import datetime
import logging
import sys
from typing import NoReturn

from serial import Serial

from port_handler import get_comport_list

logging.getLogger("asyncio").setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',
                    filename=f'../logs/UART_{datetime.date.today()}.log',
                    level=logging.DEBUG)


class UARTReceiver:
    def __init__(self, timeout: int = 0, port: str = 'COM3', baud_rate: int = 921600):
        self.timeout = timeout
        self.port = port
        self.baud_rate = baud_rate
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

    async def process_serial_port(self) -> NoReturn:
        data_line_number = 0
        if self.serial_port:
            while True:
                if self.serial_port.readable():
                    if data_line_number == 0:
                        logging.info('Start Data Receive')
                    try:
                        received_value = self.serial_port.readline()
                        data_line_number += 1
                        print(int(received_value))  # output
                        await asyncio.sleep(0)
                    except Exception as e:
                        logging.error(f'Process Error: {e}')
                        self.terminate()
                    except asyncio.CancelledError:
                        logging.info('Finish')
                        self.serial_port.close()
                        break
                else:
                    break

    async def set_timeout(self) -> bool:
        await asyncio.sleep(self.timeout)
        return True

    async def supervisor(self) -> bool:
        uart_serializer = asyncio.create_task(self.process_serial_port())
        print('[start serializer]:', uart_serializer)
        await_done = await self.set_timeout()
        if await_done is True:
            uart_serializer.cancel()
        return True

    def do_process(self) -> NoReturn:
        loop = asyncio.get_event_loop()
        loop_done = loop.run_until_complete(self.supervisor())
        if loop_done:
            loop.close()

    @staticmethod
    def terminate():
        logging.warning('FORCE SHUTDOWN SYSTEM')
        sys.exit()


if __name__ == '__main__':
    comport = get_comport_list()
    uart = UARTReceiver(timeout=2, port=comport, baud_rate=921600)
    uart.do_process()
