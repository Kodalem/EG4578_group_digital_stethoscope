# External imports
import asyncio
import os
import time
import I2S
import machine
import pimoroni_i2c
from machine import Pin, SPI
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
from pimoroni import Button
from sdcard import SDCard
from ulab import numpy as np

##################
# Display Setup  #
##################
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

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)


line_pen = display.create_pen(255, 255, 255)

# print(display.get_bounds())
max_width, max_height = display.get_bounds()

# Internal imports
import wav_lib
import real_time_display
import kalman_filter
asyncio.create_task(real_time_display.init_graph_array())

#######################
# Setup I2S for Audio #
#######################
BUFFER_SIZE = 1000000
RECORD_TIME_IN_SECONDS = 30
BITS_PER_SAMPLE = 32
SAMPLE_RATE = 48000
FORMAT = I2S.MONO

# I2S Audio file configuration
format_to_channels = {I2S.MONO: 1, I2S.STEREO: 2}
NUM_CHANNELS = format_to_channels[FORMAT]
WAV_SAMPLE_SIZE_IN_BYTES = SAMPLE_RATE // 8
RECORDING_SIZE_IN_BYTES = (
        RECORD_TIME_IN_SECONDS * SAMPLE_RATE * WAV_SAMPLE_SIZE_IN_BYTES * NUM_CHANNELS
)

###########################
# I2S Input Configuration #
###########################
I2S_ID_audio_in = 0
SCK_PIN_audio_in = 16
WS_PIN_audio_in = 17
SD_PIN_audio_in = 18

audio_in = I2S(
    I2S_ID_audio_in,
    sck=Pin(SCK_PIN_audio_in),
    ws=Pin(WS_PIN_audio_in),
    sd=Pin(SD_PIN_audio_in),
    mode=I2S.RX,
    bits=BITS_PER_SAMPLE,
    format=FORMAT,
    rate=SAMPLE_RATE,
    ibuf=BUFFER_SIZE,
)

##################################
# I2S Audio Output Configuration #
##################################
SCK_PIN_audio_out = 10
WS_PIN_audio_out = 11
SD_PIN_audio_out = 9
I2S_ID_audio_out = 0

audio_out = I2S(
    I2S_ID_audio_out,
    sck=Pin(SCK_PIN_audio_out),
    ws=Pin(WS_PIN_audio_out),
    sd=Pin(SD_PIN_audio_out),
    mode=I2S.TX,
    bits=BITS_PER_SAMPLE,
    format=FORMAT,
    rate=SAMPLE_RATE,
    ibuf=BUFFER_SIZE,
)

#################
# Setup SD Card #
#################

CS_PIN_sd = 13
SCK_PIN_sd = 14
SDO_PIN_sd = 15
SDI_PIN_sd = 12

cs = Pin(CS_PIN_sd, machine.Pin.OUT)
sd_spi = SPI(
    1,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    bits=8,
    firstbit=machine.SPI.MSB,
    sck=Pin(SCK_PIN_sd),
    mosi=Pin(SDO_PIN_sd),
    miso=Pin(SDI_PIN_sd),
)
sd = SDCard(sd_spi, cs)
sd.init_spi(25_000_000)
os.mount(sd, "/sd")

##########################
# Setup the stream array #
##########################
AudioSpecAnalBuffer = pow(2, 11)
AudioData = np.arange(0, 2 * BUFFER_SIZE, 2) # Wave
AudioFreq = np.arange(0, SAMPLE_RATE, BUFFER_SIZE) # Frequency
AmplitudeLimit = max_height


async def record_mode(audio_i2s_in):
    real_time_display.corner_print_text("Recording", 0, 0)
    # Create a blank .wav file with the epoch time appended onto it
    wav_file = open("audio_recording_{}.wav".format(time.time()), "wb")
    recording_time_seconds = 30
    record = asyncio.create_task(wav_lib.record_wav_to_sdcard(audio_i2s_in, recording_time_seconds, wav_file))
    # Display that recording completed on the display
    real_time_display.corner_print_text("Recording Completed!", 0, 0)

async def un_filtered_playback_mode(audio_i2s_in, audio_i2s_out):
    audio_i2s_out.write(audio_i2s_in.readinto(AudioSpecAnalBuffer))

async def filtered_playback_mode(audio_i2s_in, audio_i2s_out):
    audio_input_data = audio_i2s_in.readinto(AudioSpecAnalBuffer)
    audio_input_data_np = np.frombuffer(audio_input_data, dtype='h')

    # Kalman filter the audio data
    filter_audio = asyncio.create_task(kalman_filter.shark_filter(audio_input_data_np))

    # Write the filtered audio data to the output
    filtered_audio_data = await filter_audio

    audio_i2s_out.write(filtered_audio_data.tobytes())

async def fft_plot_mode(audio_i2s_in):
    audio_input_data = audio_i2s_in.readinto(AudioSpecAnalBuffer)
    audio_input_data_np = np.frombuffer(audio_input_data, dtype='h')

    # Compute the frequency response of the audio data
    real_time_display.fft_plot(audio_input_data_np, SAMPLE_RATE, AudioSpecAnalBuffer)

async def main_loop():
    # Main loop to run the audio recording and playback
    while True:
        # Check if button A is pressed
        if button_a.is_pressed():
            # Record mode
            await record_mode(audio_in)
        # Check if button B is pressed
        elif button_b.is_pressed():
            # Do nothing
            pass
            # Filtered record mode
            # await record_mode(audio_in)
        # Check if button X is pressed
        elif button_x.is_pressed():
            # Check and cancel the filtered playback mode coroutine
            try:
                if fil_mode.done():
                    fil_mode.cancel()
            except NameError:
                pass
            # Unfiltered playback mode
            unfil_playback_mode = asyncio.create_task(un_filtered_playback_mode(audio_in, audio_out))
        # Check if button Y is pressed
        elif button_y.is_pressed():
            # Check and cancel the unfiltered playback mode coroutine
            try:
                if unfil_playback_mode.done():
                    unfil_playback_mode.cancel()
            except NameError:
                pass
            # Filtered playback mode
            fil_mode = asyncio.create_task(filtered_playback_mode(audio_in, audio_out))
        # Check if button X and Y are pressed
        elif button_x.is_pressed() and button_y.is_pressed():
            # Exit the program
            break
        elif button_a.is_pressed() and button_b.is_pressed():
            # FFT plot mode
            plot_mode = asyncio.create_task(fft_plot_mode(audio_in))


# MAIN LOOP
try:
    asyncio.run(main_loop())
finally:
    # Unmount the SD card
    os.umount("/sd")
    # Close the SD card
    sd.deinit_spi()
    # Close the audio input
    audio_in.deinit()
    # Clear asynchronous tasks
    asyncio.new_event_loop()



