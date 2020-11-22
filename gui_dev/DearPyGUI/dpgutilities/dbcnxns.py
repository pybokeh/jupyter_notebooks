from dearpygui.core import *
from dearpygui.simple import *


def fetch_last_name_results(sender, data):
    pass


def fetch_locker_info(sender, data):
    print(f"From sender: {sender}")
    print(f'Sending back locker info: {get_value("last_name_locker_search")}')
