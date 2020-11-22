from dearpygui.core import *
from dearpygui.simple import *
import pandas as pd

set_main_window_pos(x=0, y=0)

def file_picker(sender, data):
    open_file_dialog(callback=apply_selected_file, extensions=".csv,.xlsx")

def apply_selected_file(sender, data):
    directory = data[0]
    file = data[1]
    set_value("directory", directory)
    set_value("file", file)
    set_value("file_path", f"{directory}\\{file}")
    if 'csv' in file.split(".")[-1]:
        df = pd.read_csv(f'{directory}\\{file}')
        with window("DataFrame Viewer"):
            add_table("DataFrame", headers=df.columns.tolist())
            for row in df[:100].values:
                add_row("DataFrame", row.tolist())
    else:
        df = pd.read_excel(f'{directory}\\{file}')

with window("DataFrame Viewer", width=400, height=400, x_pos=0, y_pos=0):
    add_button(name='openFile', callback=file_picker, label="Open file...")
    add_text("File Path: ")
    add_same_line()
    add_label_text("##filepath", source="file_path", color=[255, 0, 0])

start_dearpygui()
