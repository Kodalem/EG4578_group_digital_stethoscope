import pimoroni_i2c
import breakout_vl53l5cx
import asyncio
import time
import math

from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
from pimoroni import RGBLED

# from ulab import numpy as np

SAMPLING_RATE = 48000

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
PINS_PICO_EXPLORER = {"sda": 20, "scl": 21}

graph_array = []

# Sensor startup time is proportional to i2c baudrate
i2c = pimoroni_i2c.PimoroniI2C(**PINS_BREAKOUT_GARDEN, baudrate=2_000_000)

# Display setup, check your own following display type, default is LCD 240x240
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332)
display.set_backlight(1.0)
BG = display.create_pen(40, 40, 40)
display.set_pen(BG)

line_pen = display.create_pen(255, 255, 255)

print(display.get_bounds())
max_width, max_height = display.get_bounds()


# display.line(0, 0, 240, 230)
# display.update()


def vu_audio_data_sampling(data):
    # Calculate the mean of the microphone data
    mean = sum(data) / len(data)
    # Subtract and normalise the output
    return [int((x - mean) / 1000) for x in data]


def peak_to_peak(data):
    return max(data) - min(data)


# Function to initialise the middle line graph of the display
def init_graph_line(pixel_width=2):
    display.set_pen(BG)
    display.clear()
    display.set_pen(line_pen)
    display.line(0, 0, max_width, 0, pixel_width)
    display.update()


# Function to initialise the graph array for the plotted data
def init_graph_array():
    for i in range(max_width):
        graph_array.append(0)


async def update_graph_array(value):
    # Insert the new value at the beginning of the array.
    # and remove the last value.
    # print(value)
    graph_array.insert(0, value)
    graph_array.pop()


# Function to draw the graph from the recorded audio
async def draw_plot_realtime_axis(y_axis, baseline=max_height // 2, line_thinkness=1, h=0, s=0, v=1):
    # Clear the display

    # start_time = time.time_ns()

    display.set_pen(BG)
    display.clear()
    line_pen = display.create_pen_hsv(h, s, v)
    display.set_pen(line_pen)
    # Draw the graph line from the graph array
    asyncio.create_task(update_graph_array(y_axis))

    # end_time = time.time_ns()
    # elapsed_time = end_time - start_time
    # print(elapsed_time / 10**6)

    # Enumerate the graph array to draw the graph line
    for i, y in enumerate(graph_array):
        # print(i,y)
        # display.pixel(i, y)
        # At the end of the graph array, break the loop
        if i == max_width - 1:
            break
        display.line(i, y + baseline, (i + 1), graph_array[i + 1] + baseline, line_thinkness)
    # Update the display
    display.update()

# Probably a bad idea to use this function
async def draw_plot_realtime_axis_better(y_axis, y_axis_future, x_axis, x_axis_future, baseline=max_height // 2, line_thinkness=1, h=0, s=0, v=1):
    # Clear the display

    # start_time = time.time_ns()

    # If the x_axis_future is greater than the max_width...
    if x_axis_future > max_width:
        divisor = x_axis_future / max_width
        x_axis = x_axis - max_width*math.floor(divisor)
        x_axis_future = x_axis_future - max_width*math.floor(divisor)
        # If the divisor is not a whole number, clear the display
        if divisor % 1 != 0:
            display.set_pen(BG)
            display.clear()


    display.set_pen(BG)
    #display.clear()
    line_pen = display.create_pen_hsv(h, s, v)
    display.set_pen(line_pen)
    # Draw the graph line from the graph array
    asyncio.create_task(update_graph_array(y_axis))

    # end_time = time.time_ns()
    # elapsed_time = end_time - start_time
    # print(elapsed_time / 10**6)

    # Draw the graph line
    display.line(x_axis, y_axis+baseline, x_axis_future, y_axis_future+baseline, line_thinkness)


    # Update the display
    display.update()


# Self function runner to test the graph plotting from this python file
if __name__ == "__main__":
    import random
    import time

    init_graph_line()
    init_graph_array()
    while True:
        draw_plot_realtime_axis(random.randint(0, max_height // 2))
        time.sleep(0.1)
