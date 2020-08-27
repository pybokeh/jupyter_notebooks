# pip install mplcyberpunk
import mplcyberpunk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use("cyberpunk")

plt.plot([], [], marker='o', label='CPU %')


def animate(i):
    data = pd.read_csv('data.csv')
    x = data['x_value']
    y = data['cpu_perc']

    ax = plt.gca()
    line = ax.lines

    line[0].set_data(x, y)
    line[0].set_linewidth(2)

    xlim_low, xlim_high = ax.get_xlim()
    ylim_low, ylim_high = ax.get_ylim()
    
    ax.set_xlim(left=max(0, x.max()-50), right=x.max()+5)
    
    # Run this line instead if you want the left xlim to be fixed at zero
    # ax.set_xlim(xlim_low, (x.max() + 5))

    current_ymin = y.min()
    current_ymax = y.max()

    ax.set_ylim((current_ymin - 5), (current_ymax + 5))
    
    mplcyberpunk.add_underglow()
    
    # Unfortunately, this effect does not work when using animation
    # Set a higher linewidth as a workaround
    # mplcyberpunk.make_lines_glow()


ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.legend()
plt.tight_layout()
plt.show()
