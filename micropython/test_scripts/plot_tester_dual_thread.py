from display_plotter import *
from math import *
import asyncio
import random
import time

init_graph_line()
init_graph_array()
import _thread

n = 1
sLock = _thread.allocate_lock()
y_value = 0


def CoreTask():
    # asyncio.run(draw_plot_realtime_axis(random.randint(0, max_height//2)))
    # time.sleep(0.1)
    # print("Print line")
    print("Entering into the second thread...")
    sLock.acquire()
    print("Entered into the second thread...")

    Fs = 7600
    f = 25
    sample = 16
    y_value = int(50 * (sin(2 * pi * f * n / Fs)))
    # print(y_value)
    asyncio.run(draw_plot_realtime_axis(y_value, line_thinkness=3))
    n = n + 1

    print("Exiting out of the second thread...")
    sLock.release()


# Start the core task
_thread.start_new_thread(CoreTask, ())

while True:
    # asyncio.run(draw_plot_realtime_axis(random.randint(0, max_height//2)))
    # time.sleep(0.1)
    # print("Print line")
    print("Entering into the main thread...")
    sLock.acquire()
    print("Entered into the main thread...")

    start_time = time.time_ns()

    asyncio.run(draw_plot_realtime_axis(y_value, line_thinkness=3))

    end_time = time.time_ns()

    print("Exiting out of the second thread...")
    sLock.release()



