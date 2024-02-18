
from machine import I2S
from machine import Pin
import math
import struct
import uasyncio as asyncio


## I2S Audio Output Configuration
SCK_PIN = 10
WS_PIN = 11
SD_PIN = 9
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 2000
SAMPLE_RATE = 48000
BITS_PER_SAMPLE = 32

def make_tone(rate, bits, frequency):
    # create a buffer containing the pure tone samples
    samples_per_cycle = rate // frequency
    sample_size_in_bytes = bits // 8
    samples = bytearray(samples_per_cycle * sample_size_in_bytes)
    volume_reduction_factor = 32
    range = pow(2, bits) // 2 // volume_reduction_factor

    if bits == 16:
        format = "<h"
    else:  # assume 32 bits
        format = "<l"

    for i in range(samples_per_cycle):
        sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
        struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

    return samples


## Tone generation configuration
TONE_FREQUENCY_IN_HZ = 25

samples = make_tone(SAMPLE_RATE, BITS_PER_SAMPLE, TONE_FREQUENCY_IN_HZ)

audio_out = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.TX,
    bits=BITS_PER_SAMPLE,
    format=I2S.MONO,
    rate=SAMPLE_RATE,
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

# Play the tone
async def play_tone(samples):
    num_written = audio_out.write(samples)
    #print("wrote {} bytes".format(num_written))

try:
    while True:
        asyncio.run(play_tone(samples))

except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))

# cleanup
audio_out.deinit()
print("Done")

