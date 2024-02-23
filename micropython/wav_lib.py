from sdcard import SDCard
from machine import SPI
import asyncio
import os

def create_wav_header(sampleRate, bitsPerSample, num_channels, num_samples):
    data_size = num_samples * num_channels * bitsPerSample // 8
    byte_header = bytes("RIFF", "ascii")  # RIFF Marking (4byte)
    byte_header += (data_size + 36).to_bytes(4, "little")  # File size, excluding first 8 bytes of header (4byte)
    byte_header += bytes("WAVE", "ascii")  # File type
    byte_header += bytes("fmt ", "ascii")  # Format Chunk Marker
    byte_header += (16).to_bytes(4, "little")  # Length of format data
    byte_header += (1).to_bytes(2, "little")  # Format type (1 - PCM)
    byte_header += (num_channels).to_bytes(2, "little") # Number of channels if it is mono or stereo (2byte)
    byte_header += (sampleRate).to_bytes(4, "little")  # Sample Rate (4byte)
    byte_header += (sampleRate * num_channels * bitsPerSample // 8).to_bytes(4, "little") # Audio data rate (4byte)
    byte_header += (num_channels * bitsPerSample // 8).to_bytes(2, "little")  # Block alignment (2byte)
    byte_header += (bitsPerSample).to_bytes(2, "little")  # Number of bits per sample (2byte)
    byte_header += bytes("data", "ascii")  # ASCII Data Chunk Marker (4byte)
    byte_header += (data_size).to_bytes(4, "little")  # Number of bytes of data, its size in bytes (4byte)
    return byte_header


async def record_wav_to_sdcard(SD_spi, sreader, wav, SAMPLE_RATE_IN_HZ, WAV_SAMPLE_SIZE_IN_BITS, NUM_CHANNELS, RECORD_TIME_IN_SECONDS, RECORDING_SIZE_IN_BYTES):
    # create header for WAV file and write to SD card
    wav_header = create_wav_header(
        SAMPLE_RATE_IN_HZ,
        WAV_SAMPLE_SIZE_IN_BITS,
        NUM_CHANNELS,
        SAMPLE_RATE_IN_HZ * RECORD_TIME_IN_SECONDS,
    )
    num_bytes_written = wav.write(wav_header)

    # allocate sample array
    # memoryview used to reduce heap allocation
    mic_samples = bytearray(10000)
    mic_samples_mv = memoryview(mic_samples)

    num_sample_bytes_written_to_wav = 0

    # continuously read audio samples from I2S hardware
    # and write them to a WAV file stored on a SD card
    print("Recording size: {} bytes".format(RECORDING_SIZE_IN_BYTES))
    print("==========  START RECORDING ==========")
    while num_sample_bytes_written_to_wav < RECORDING_SIZE_IN_BYTES:
        # read samples from the I2S peripheral
        num_bytes_read_from_mic = await sreader.readinto(mic_samples_mv)
        # write samples to WAV file
        if num_bytes_read_from_mic > 0:
            num_bytes_to_write = min(
                num_bytes_read_from_mic, RECORDING_SIZE_IN_BYTES - num_sample_bytes_written_to_wav
            )
            num_bytes_written = wav.write(mic_samples_mv[:num_bytes_to_write])
            num_sample_bytes_written_to_wav += num_bytes_written

    print("==========  DONE RECORDING ==========")


    # cleanup
    #wav.close()
    #os.umount("/sd")
    #SD_spi.deinit()
    #audio_in.deinit()
