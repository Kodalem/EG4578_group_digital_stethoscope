# External imports
import os
import asyncio
import I2S
import machine
import time
from machine import Pin, SPI
from sdcard import SDCard

# Internal imports
import wav_lib
import audio_output
import real_time_display
import audio_analysis

#######################
# Setup I2S for Audio #
#######################
BUFFER_SIZE = 24000
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


async def main_loop():

    # Use epoch time and append it to the file name
    epoch_time = time.time()
    file_name = "/sd/recording_{}.wav".format(epoch_time)

    # Record audio to SD card
    print("Recording audio to SD card")
    wav = open(file_name, "wb")

    # Create a stream reader of the audio input
    stream_reader = asyncio.StreamReader(audio_in)

    # Get the frequency response of the audio input
    frequency_biases, magnitude = audio_analysis.frequency_response(stream_reader, SAMPLE_RATE)
    # Graph the frequency response
    graph_fft = asyncio.create_task(real_time_display.plot_frequency_response(frequency_biases, magnitude))

    wav_recording = asyncio.create_task(wav_lib.record_wav_to_sdcard(sd_spi, stream_reader, wav, SAMPLE_RATE, BITS_PER_SAMPLE, NUM_CHANNELS, RECORD_TIME_IN_SECONDS, RECORDING_SIZE_IN_BYTES))
    wav_playback = asyncio.create_task(audio_output.playback_i2s(audio_out, stream_reader))





