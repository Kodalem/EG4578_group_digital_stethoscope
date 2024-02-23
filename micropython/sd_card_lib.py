from sdcard import SDCard
from machine import SPI, Pin
import machine
import wav_lib
import os

def create_file_wav(filename: str):
    wav = open("/sd/{}".format(filename), "wb")
    return wav


