from dearpygui.core import *
from dearpygui.simple import *
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn
sns.set_theme(style="ticks")

set_theme("Cherry")

# Set main window's properties
set_main_window_title("Seaborn Chart Viewer")
set_main_window_pos(x=0, y=0)


def seaborn_plot_window(sender, data):
    with window("Chart Window", width=700, height=500, on_close=close_seaborn_window):
        add_drawing("canvas", width=700, height=500, parent="Chart Window")

        # Initialize the figure with a logarithmic x axis
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.set_xscale("log")

        # Load the example planets dataset
        planets = sns.load_dataset("planets")

        # Plot the orbital period with horizontal boxes
        sns.boxplot(
            x="distance",
            y="method",
            data=planets,
            whis=[0, 100],
            width=0.6,
            palette="vlag",
        )

        # Add in points to show each observation
        sns.stripplot(
            x="distance", y="method", data=planets, size=4, color=".3", linewidth=0
        )

        # Tweak the visual presentation
        ax.xaxis.grid(True)
        ax.set(ylabel="")
        sns.despine(trim=True, left=True)
        plt.savefig("boxplot_jitter.png", bbox_inches="tight")
        plt.close(fig)

        clear_drawing("canvas")
        draw_image("canvas", "boxplot_jitter.png", [0, 0], pmax=[600, 450])


def close_seaborn_window(sender, data):
    delete_item("Chart Window")


with window("Main", x_pos=0, y_pos=0):
    add_button(name="BoxPlot /w Jitter", callback=seaborn_plot_window)

start_dearpygui()
