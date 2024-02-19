import os
import time
import uasyncio as asyncio
from machine import I2S
from machine import Pin

# I2S configuration
I2S_ID = 0
SCK_PIN = 14
WS_PIN = 15
SD_PIN = 16
BUFFER_SIZE = 24000
SAMPLE_RATE = 48000
BITS_PER_SAMPLE = 32


async def record_audio(audio_in):
    audio_in = I2S(I2S_ID,sck=Pin(SCK_PIN),
                   ws=Pin(WS_PIN), sd=Pin(SD_PIN),
                   mode=I2S.RX, bits=BITS_PER_SAMPLE,
                   format=I2S.MONO, rate=SAMPLE_RATE,
                   ibuf = BUFFER_SIZE)
    data = audio_in.read(BUFFER_SIZE)
    return data

