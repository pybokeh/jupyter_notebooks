from dearpygui.core import *
from dearpygui.simple import *
from dpgutilities import dbcnxns


def show_update_locker_screen(sender, data):
    with window(
        "Update Locker Info", width=600, height=400, on_close=close_locker_screen
    ):
        add_spacing(count=10)
        add_text("Enter last name:")
        add_same_line()
        add_input_text(
            name="last_name_locker_search",
            label="",
            source="last_name_locker_search"
        )
        add_same_line()
        add_button(
            name="locker_search_button",
            label="Search",
            callback=dbcnxns.fetch_locker_info,
        )


def show_update_desk_screen(sender, data):
    with window("Update Desk Info", width=600, height=400, on_close=close_desk_screen):
        add_spacing(count=10)
        add_text("Enter last name:")
        add_same_line()
        add_input_text(
            name="last_name_desk_search",
            label="",
            source="last_name_desk_search"
        )
        add_same_line()
        add_button(
            name="desk_search_button",
            label="Search",
            callback=dbcnxns.fetch_desk_info,
        )


def show_update_devices_screen(sender, data):
    with window(
        "Update Mobile Devices Info",
        width=600,
        height=400,
        on_close=close_devices_screen,
    ):
        add_spacing(count=10)
        add_text("Enter last name:")
        add_same_line()
        add_input_text(
            name="last_name_devices_search",
            label="",
            source="last_name_devices_search"
        )
        add_same_line()
        add_button(
            name="devices_search_button",
            label="Search",
            callback=dbcnxns.fetch_devices_info,
        )


def show_update_assets_screen(sender, data):
    with window(
        "Update Assets Info", width=600, height=400, on_close=close_assets_screen
    ):
        add_spacing(count=10)
        add_text("Enter last name:")
        add_same_line()
        add_input_text(
            name="last_name_assets_search",
            label="",
            source="last_name_assets_search"
        )
        add_same_line()
        add_button(
            name="assets_search_button",
            label="Search",
            callback=dbcnxns.fetch_assets_info,
        )


def close_locker_screen(sender, data):
    delete_item("Update Locker Info")


def close_desk_screen(sender, data):
    delete_item("Update Desk Info")


def close_devices_screen(sender, data):
    delete_item("Update Mobile Devices Info")


def close_assets_screen(sender, data):
    delete_item("Update Assets Info")
