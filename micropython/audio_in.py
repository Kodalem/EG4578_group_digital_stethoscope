import asyncio
import I2S
import machine
import wav_lib


async def record_audio(I2S_audio_in):
    sreader = asyncio.StreamReader(I2S_audio_in)

async def stop_recording(I2S_audio_in):
    I2S_audio_in.deinit()