from display_plotter import *
from math import *
import asyncio
import random
import time

init_graph_line()
init_graph_array()

n = 1
h = 0
h_step = 0.001

while True:
    # asyncio.run(draw_plot_realtime_axis(random.randint(0, max_height//2)))
    # time.sleep(0.1)
    # print("Print line")

    # start_time = time.time_ns()

    Fs = 5600
    f = 220
    sample = 16
    y_value = int(100 * (sin(2 * pi * f * n / Fs)))

    # end_time = time.time_ns()
    # elapsed_time = end_time - start_time
    # print(elapsed_time / 10**6)

    # print(y_value)

    # start_time = time.time_ns()

    asyncio.run(draw_plot_realtime_axis(y_value, line_thinkness=3, h=h, s=1, v=1))

    # end_time = time.time_ns()
    # elapsed_time = end_time - start_time
    # print(elapsed_time / 10**6)
    h = h + h_step

    if (h >= 1):
        h = 0

    n = n + 1




