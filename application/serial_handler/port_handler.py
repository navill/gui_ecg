import platform

from serial.tools import list_ports

COM = {
    'win': 'CP210x',
    'mac': 'CP2102'
}


def check_os():
    platform_name = platform.system()
    if platform_name == 'Darwin':
        return 'mac'
    elif platform_name == 'Windows':
        return 'win'


def get_valid_comport() -> str:
    os_flag = check_os()
    comport_set = list_ports.comports()
    for comport in comport_set:
        if COM[os_flag] in comport.description:
            print(comport.description)
            return str(comport.device)
