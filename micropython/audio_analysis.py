import time
import math
from ulab import numpy as np

def frequency_response(data, sampling_rate):
    # Perform FFT on the data
    fft_data = np.fft.fft(data)
    # Calculate the frequency biases
    frequency_biases = np.fft.fftfreq(len(data), 1 / sampling_rate)
    # Calculate the magnitude of the FFT
    magnitude = np.abs(fft_data)
    # Return the frequency bins and the magnitude
    return frequency_biases, magnitude

def non_linear_kalman_filter(data, initial_state, initial_covariance, process_noise, measurement_noise):
    # Initialise the state and covariance
    state = initial_state
    covariance = initial_covariance
    # Initialise the output
    output = []
    # Iterate over the data
    for measurement in data:
        # Predict the next state
        predicted_state = state
        predicted_covariance = covariance + process_noise
        # Calculate the Kalman gain
        kalman_gain = predicted_covariance / (predicted_covariance + measurement_noise)
        # Update the state and covariance
        state = predicted_state + kalman_gain * (measurement - predicted_state)
        covariance = (1 - kalman_gain) * predicted_covariance
        # Append the state to the output
        output.append(state)
    # Return the output
    return output


def vu_audio_data_sampling(data):
    # Calculate the mean of the microphone data
    mean = sum(data) / len(data)
    # Subtract and normalise the output
    return [int((x - mean) / 1000) for x in data]


def peak_to_peak(data):
    return max(data) - min(data)