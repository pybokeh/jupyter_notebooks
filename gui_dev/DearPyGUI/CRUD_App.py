from dearpygui.core import *
from dearpygui.simple import *
from dpgutilities import dpgwindows as dpgw

set_theme("Cherry")


# Set main window's properties
set_main_window_title("SC Roster Application")
set_main_window_pos(x=0, y=0)


with window("Main Menu", width=400, height=400, x_pos=0, y_pos=0):
    add_spacing(count=20)
    add_button(
        "update_locker",
        label="Update Locker Info",
        callback=dpgw.show_update_locker_screen,
    )
    add_spacing(count=10)
    add_button(
        "update_desk", label="Update Desk Info", callback=dpgw.show_update_desk_screen
    )
    add_spacing(count=10)
    add_button(
        "update_devices",
        label="Update Mobile Devices Info",
        callback=dpgw.show_update_devices_screen,
    )
    add_spacing(count=10)
    add_button(
        "update_assets",
        label="Update Assets Info",
        callback=dpgw.show_update_assets_screen,
    )

start_dearpygui()
