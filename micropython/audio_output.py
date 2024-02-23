
# Play the tone
async def playback_i2s(I2S_output, i2s_data_out):
    I2S_output.write(i2s_data_out)

