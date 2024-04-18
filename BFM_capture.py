import sys
import pandas as pd
import time
from datetime import datetime
import numpy as np
import os
from scipy.io import savemat
NSUBC_VALID = 234
NSUBC_VALID_S = 23  #Considering the real-time performance, the current program only outputs 23 subcarriers of BFM

def decompress(bfm_angles, Nc, Nr, NSUBC_VALID, phi_bit, psi_bit):
    const1_phi = 1 / (2 ** (phi_bit - 1))
    const2_phi = 1 / (2 ** phi_bit)
    phi_11 = np.pi * (const2_phi + const1_phi * bfm_angles[:, 0])
    phi_21 = np.pi * (const2_phi + const1_phi * bfm_angles[:, 1])
    phi_31 = np.pi * (const2_phi + const1_phi * bfm_angles[:, 2])

    const1_psi = 1 / (2 ** (psi_bit + 1))
    const2_psi = 1 / (2 ** (psi_bit + 2))
    psi_21 = np.pi * (const2_psi + const1_psi * bfm_angles[:, 3])
    psi_31 = np.pi * (const2_psi + const1_psi * bfm_angles[:, 4])
    psi_41 = np.pi * (const2_psi + const1_psi * bfm_angles[:, 5])
    
    v_matrix = np.zeros((Nc, NSUBC_VALID, Nr), dtype=np.complex128)
    for s_i in range(NSUBC_VALID):
        D_1 = np.array([[np.exp(1j * phi_11[s_i]), 0, 0, 0],
                        [0, np.exp(1j * phi_21[s_i]), 0, 0],
                        [0, 0, np.exp(1j * phi_31[s_i]), 0],
                        [0, 0, 0, 1]])

        G_21 = np.array([[np.cos(psi_21[s_i]), np.sin(psi_21[s_i]), 0, 0],
                         [-np.sin(psi_21[s_i]), np.cos(psi_21[s_i]), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

        G_31 = np.array([[np.cos(psi_31[s_i]), 0, np.sin(psi_31[s_i]), 0],
                         [0, 1, 0, 0],
                         [-np.sin(psi_31[s_i]), 0, np.cos(psi_31[s_i]), 0],
                         [0, 0, 0, 1]])

        G_41 = np.array([[np.cos(psi_41[s_i]), 0, 0, np.sin(psi_41[s_i])],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [-np.sin(psi_41[s_i]), 0, 0, np.cos(psi_41[s_i])]])

        I_matrix = np.eye(Nr, Nc)
        Vtemp = np.matmul(D_1, np.matmul(G_21.T, np.matmul(G_31.T, np.matmul(G_41.T, I_matrix))))
        v_matrix[:, s_i, :] = np.transpose(Vtemp)
    v_matrix = np.transpose(v_matrix, (2, 0, 1))
   
    return np.round(v_matrix, decimals=4)




def hexStr2binStr(hexStr):
    dec = int(hexStr, 16)
    bl = len(hexStr) * 4
    binStr = "{:0{}b}".format(dec, bl)
    return binStr[::-1]

def packet_extract(original_bfm, packet_timestamp, packet_snr, ether_src): 
    BFA = []
    BFA_binStr = ''
    for i in range(NSUBC_VALID+1):
        BFA.append([])
        if i>=1:
            for j in range(6):
                temp = 2*((i-1)*6+j)
                angle = hexStr2binStr(original_bfm[temp:temp+2])
                BFA_binStr = BFA_binStr + angle            
    for i in range(NSUBC_VALID+1):
        if i==0:
            BFA[i].append(packet_timestamp)
            BFA[i].append(int(packet_snr,16))
            BFA[i].append(str(ether_src))
            for j in range(3):
                BFA[i].append(0)
        else:
            for j in range(3):
                temp = 48*(i-1)+9*j
                tempstr = BFA_binStr[temp:temp+9]
                tempstr = tempstr[::-1]
                BFA[i].append(int(tempstr, 2))
            for j in range(3):
                temp = 48*(i-1)+7*j+27
                tempstr = BFA_binStr[temp:temp+7]
                tempstr = tempstr[::-1]
                BFA[i].append(int(tempstr, 2))
    
    return BFA

def read_packets():
    bfm_buffer = []  
    start_time = time.time()
    data_path='./BFM_data'
    if os.path.exists(data_path):
        print(f'Folder {data_path} exists!')
    else:   
        os .mkdir('./BFM_data')
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            fields = line.strip().split('\t')
            if len(fields) == 4:
                frame_time_relative, wlan_sa, wlan_da, wlan_vht_compressed_beamforming_report = fields
                beamforming_report=str(wlan_vht_compressed_beamforming_report)
                packet_snr = beamforming_report[:2]
                original_bfm = beamforming_report[2:-123]
                ether_src = wlan_sa
                packet_timestamp = frame_time_relative
                BFA = packet_extract(original_bfm, packet_timestamp, packet_snr, ether_src)
                BFA_S = BFA[0:234:10] # select 23 subcarriers
                bfm_angles = np.array([row for i, row in enumerate(BFA_S) if i > 0])  
                if bfm_angles.shape[0] == NSUBC_VALID_S:
                    packet_info = decompress(bfm_angles, 1, 4, NSUBC_VALID_S, 9, 7)
                    bfm = [packet_timestamp, packet_snr, ether_src, packet_info]
                    bfm_buffer.append(bfm)

                if time.time() - start_time >= 1:
   
                    data_to_save = {
                        'packet_timestamps': [item[0] for item in bfm_buffer],
                        'packet_snrs': [item[1] for item in bfm_buffer],
                        'ether_srcs': [item[2] for item in bfm_buffer],
                        'packet_infos': [item[3] for item in bfm_buffer]  
                    }
                    file_name = f"./BFM_data/packets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mat"
                    file_path = file_name   
                    savemat(file_path, data_to_save)
                    bfm_buffer = []  
                    start_time = time.time() 
                
    except KeyboardInterrupt:
        print("The program is interrupted by the user.")

if __name__ == "__main__":
    read_packets()





