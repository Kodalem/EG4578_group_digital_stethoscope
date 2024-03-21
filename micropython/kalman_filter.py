import asyncio
from machine import I2C, Pin
import time
import math
from ulab import numpy as np
"""
Kalman Filter Setup
"""

# State transition matrix (yeah, it's just one dimensional lol... lmao)
def state_transition_matrix():
    return np.array([[1]])

def calculate_coefficient(forgetting_factor, step_count):
    amnestic_factor = (1 - forgetting_factor) / (1 + forgetting_factor ** step_count)
    return amnestic_factor

def new_measurement_noise_info(forgetting_factor, step_count, Q_nq, q_nq, x_nq, K_nq, P_nq, v_nq):
    # Calculate the amnesic factor
    amnesic_factor = calculate_coefficient(forgetting_factor, step_count)


    F = state_transition_matrix()

    # New Q and q
    q_k = (1 - amnesic_factor) * q_nq + amnesic_factor * (x_nq - np.dot(F, x_nq))
    Q_k = (1 - amnesic_factor) * Q_nq + amnesic_factor * (K_nq * v_nq * v_nq.transpose() * K_nq.transpose() - P_nq - F*P_nq*F.transpose())

    return Q_k, q_k

def new_process_noise_info(forgetting_factor, step_count, R_np, H_np, P_np, x_np, z_np, r_np):
    # Calculate the amnesic factor
    amnesic_factor = calculate_coefficient(forgetting_factor, step_count)

    # New R
    r_k = (1 - amnesic_factor) * r_np + amnesic_factor * (z_np - np.dot(H_np, np.linalg.inv(x_np)))
    v_k = z_np - np.dot(H_np, x_np) - r_k
    R_k = (1 - amnesic_factor) * R_np + amnesic_factor * (v_k * v_k.transpose() - np.dot(H_np, np.dot(P_np, H_np.transpose())))

    return R_k, v_k


def predict_state_sage_husa(x_p, P_p, Q_p, forgetting_factor, step_count, r_p):

    ## Mesurenent covariance update adaptation
    amnesic_factor = calculate_coefficient(forgetting_factor, step_count)

    # State transition matrix (yeah, it's just one dimensional lol... lmao)
    F = np.array([[1]])

    x_p = np.dot(F, x_p) + r_p
    FPF_t = np.dot(F, np.dot(P_p, F.transpose()))
    P_p = FPF_t + Q_p

    return x_p, P_p


def adaptive_factor_function(design_constant_0, design_constant_1, h_u, P_u, R_u, x_u, z_u):
    y_u = z_u - np.dot(h_u, x_u)

    HP = np.dot(h_u, P_u)
    H_t = h_u.transpose()
    HPH_t = np.dot(HP, H_t)
    C_k = HPH_t + R_u

    difference_vector_x = np.linalg.norm(y_u)/np.sqrt(C_k)

    if (difference_vector_x > design_constant_0):
        adaptive_factor = 1
    elif (design_constant_0 >= difference_vector_x > design_constant_1):
        adaptive_factor = (design_constant_0 / difference_vector_x) * ((design_constant_1 - difference_vector_x) / difference_vector_x)
    else:
        adaptive_factor = 0

    return adaptive_factor

def update_state_sage_husa_adaptive(x_u, P_u, z_u, H_u, R_u, I_u, adaptive_factor):
    # print("P:", P_u)
    # print("H:", h_u)
    F = state_transition_matrix()

    # Calculate the Kalman gain
    K_u = (1/adaptive_factor) * np.dot(P_u, H_u.transpose()) * ((1/adaptive_factor) * np.dot(H_u, np.dot(P_u, H_u.transpose())) + R_u).inverse()

    # Update the state and covariance
    x_u = np.linalg.inv(np.dot(F.transpose,np.dot(P_u, F)) + adaptive_factor * np.linalg.inv(P_u)) * (np.dot(F.transpose, np.dot(P_u, z_u)) + adaptive_factor * np.dot(P_u, x_u))
    P_u = (1/adaptive_factor) * (I_u - np.dot(K_u, H_u)) * np.linalg.inv(P_u)

    return x_u, P_u, K_u
async def shark_filter(byte_data_np):
    # Filtered data
    filtered_data = []
    # Array dimensions
    dim_x = 1
    dim_z = 1
    # State mean
    x = np.array([[0]])
    # Covariance matrix
    P = np.array([[10]])
    # Measurement function
    H = np.array([[1]])
    # Measurement covariance, add more dimensions in diagonal for more measurements
    R = np.eye(dim_z) * 1
    # Process noise
    Q = np.eye(dim_x) * 0.0115
    # Identity matrix
    I = np.eye(dim_x)
    # Forgetting factor
    forgetting_factor = 0.66
    # Step count
    step_count = 1
    # Design constants
    design_constant_0 = 1.15
    design_constant_1 = 3.45

    # Initial process noise info series
    r = R[0]
    q = Q[0]
    # Filter each sample in the data
    for sample in byte_data_np:

        # New process noise info series
        R, v = new_process_noise_info(forgetting_factor, step_count, R, H, P, x, sample, r)
        # Predict
        x, P = predict_state_sage_husa(x, P, Q, forgetting_factor, step_count, r)
        # Calculate adaptive factor
        adaptive_factor = adaptive_factor_function(design_constant_0, design_constant_1, H, P, R, x, sample)
        # Update
        x, P, K = update_state_sage_husa_adaptive(x, P, sample, H, R, I, adaptive_factor)
        # New measurement noise info series
        Q, r = new_measurement_noise_info(forgetting_factor, step_count, Q, q, x, K, P, v)
        # Increment step count
        step_count += 1
        # Append the filtered data
        filtered_data.append(x[0])

    return filtered_data


