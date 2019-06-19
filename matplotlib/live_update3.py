# plotting just the last 20 points using deque
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def animate(i):
    global x
    x += np.abs(np.random.randn())
    y = np.random.randn()
    data.append((x, y))
    ax.relim()
    ax.autoscale_view()
    line.set_data(*zip(*data))

fig, ax = plt.subplots()
x = 0
y = np.random.randn()
data = deque([(x, y)], maxlen=20)
line, = plt.plot(*zip(*data), c='black')

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()