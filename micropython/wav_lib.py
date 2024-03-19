from sdcard import SDCard
from machine import SPI
import asyncio
import os

def create_wav_header(sampleRate, bitsPerSample, num_channels, num_samples):
    data_size = num_samples * num_channels * bitsPerSample // 8
    byte_header = bytes("RIFF", "ascii")  # RIFF Marking (4byte)
    byte_header += (data_size + 36).to_bytes(4, "little")  # File size, excluding first 8 bytes of header (4byte)
    byte_header += bytes("WAVE", "ascii")  # File type
    byte_header += bytes("fmt", "ascii")  # Format Chunk Marker
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


async def record_wav_to_sdcard(i2s_audio_in, record_time, wav_file):
    try:
        s_reader = asyncio.StreamReader(i2s_audio_in)
        # Create header for WAV file and write to SD card
        wav_header = create_wav_header(
            i2s_audio_in.rate,
            i2s_audio_in.bits,
            1 if i2s_audio_in.format == I2S.MONO else 2,
            i2s_audio_in.rate * record_time,
        )
        number_of_bytes_written = wav_file.write(wav_header)

        # Create a buffer to store audio samples
        mic_samples = bytearray(10000)
        # To allow Python to access the internal memory of audio samples
        mic_samples_mv = memoryview(mic_samples)
        number_sample_bytes_written_to_wav = 0

        # Get the size of the recording
        if i2s_audio_in.format == I2S.MONO:
            recording_size = record_time * i2s_audio_in.rate * i2s_audio_in.bits
        else:
            recording_size = record_time * i2s_audio_in.rate * i2s_audio_in.bits * 2

        # Continuously read audio samples from the I2S hardware
        # and write them onto virgin partition of the created .wav file SD card
        print("Recording size: {} bytes".format(recording_size))
        while number_sample_bytes_written_to_wav < recording_size:
            # read samples from the I2S peripheral
            num_bytes_read_from_mic = await s_reader.readinto(mic_samples_mv)
            # write samples to WAV file
            if num_bytes_read_from_mic > 0:
                num_bytes_to_write = min(
                    num_bytes_read_from_mic, recording_size - number_sample_bytes_written_to_wav
                )
                number_of_bytes_written = wav_file.write(mic_samples_mv[:num_bytes_to_write])
                number_sample_bytes_written_to_wav += number_of_bytes_written
        print("Recording complete!")
        # Close the file
        wav_file.close()
        # Return True to indicate that the recording was successful for the await
        return True
    except:
        print("Recording failed!")
        # Return False to indicate that the recording was unsuccessful for the await
        return False