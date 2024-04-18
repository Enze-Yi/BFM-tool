
# BFM Tool: Real-Time WiFi Beamforming Feedback Matrix Capture

BFM Tool is an open-source software for retrieving Wi-Fi beamforming feedback packets and reconstructing the beamforming feedback matrix (BFM) in real time. This tool is developed and built on a 4x1 MIMO WiFi configuration (e.g., AP:Netgear Nighthawk X4S AC2600 router
; STA: Tenda U10). We plan to support the BFM Tool with more MIMO configurations in the future.

# Advantages Over CSI
Different from Channel State Information (CSI) which requires modifications to hardware drivers, BFM Tool captures beamforming feedback matrix without any hardware modification. This new information enables user to rapidly deploy on devices that support MU-MIMO. To build wireless sensing applications, the user can exploit proposed BFM ratios method, offering a new technique to significantly improve the sensing performance.

# Research Background
This tool originates from the Wireless Sensing Group led by Daqing Zhang at Peking University. Our team focus on developing the fundamentals of WiFi wireless sensing and has developed a range of theories and techniques based on proposed Fresnel zone-based sensing model.

## Citation
If you find BFM Tool useful, please consider citing our associated paper:
```bibtex
@inproceedings{295679,
  author = {Enze Yi and Dan Wu and Jie Xiong and Fusang Zhang and Kai Niu and Wenwei Li and Daqing Zhang},
  title = {{BFMSense}: {WiFi} Sensing Using Beamforming Feedback Matrix},
  booktitle = {21st USENIX Symposium on Networked Systems Design and Implementation (NSDI 24)},
  year = {2024},
  address = {Santa Clara, CA},
  url = {https://www.usenix.org/conference/nsdi24/presentation/yi},
  publisher = {USENIX Association},
  month = apr
}
```

## Setup

### Hardware
- **AP**: Netgear Nighthawk X4S AC2600 router
- **Sniffer**: An A6210 WiFi USB Adapter
- **Clients**: Two Tenda U10 Network cards
- **Computers**: Two PCs configured as Server and Client

### Software
- Python 3.10
- Windows 10
- iperf3
- tshark
- WlanHelper.exe

## Usage Instructions

### 1. Establishing MU-MIMO Communication Between Server and Two Clients
Install iperf3 on both server and client machines. To establish MU-MIMO communication:
- **Server**: Execute the following commands in two separate terminals to create two server instances:
  ```
  iperf3 -s -i 1 -p <port1>
  iperf3 -s -i 1 -p <port2>
  ```
- **Client**: Execute the following commands in two separate terminals to connect to the server instances:
  ```
  iperf3 -c <server address> -B <client address> -i 1 -R -t <time> -p <port1>/<port2>
  ```

### 2. Monitor Mode Setup
Set the A6210 WiFi USB Adapter to monitor mode with these commands:
```
WlanHelper.exe "WLAN3" mode monitor
WlanHelper.exe "WLAN3" freq 5
WlanHelper.exe "WLAN3" channel <AP’s channel>
```

### 3. Capture Packets
Capture packets using tshark and save BFM data:
```
"<path of tshark>" -l -i <name of sniffer> -I -Y "(wlan.fc.type_subtype == 0x0e) && frame.len > 1000" -T fields -e frame.time_relative -e wlan.sa -e wlan.da -e wlan.vht.compressed_beamforming_report | python <path of BFM_capture.py>
```

### Data Collection and Analysis
For each BFM packet captured, we record the following information in a `.mat` file format:
- **Timestamp**: Time at which the packet was captured.
- **Source Address**: MAC address of the source device.
- **Destination Address**: MAC address of the destination device.
- **Compressed Beamforming Report**: Beamforming data collected from the packet.

Use the provided MATLAB script `readBFM.m` to parse the `.mat` files and calculate the BFM ratio.

**Parameter Descriptions**:
- `<server address>` & `<client address>`: MAC addresses of your server and client Tenda Network cards respectively.
- `<time>`: Expected duration of communication between server and client (in seconds).
- `<name of sniffer>` & `<path of BFM_capture.py>`: Specifics of your setup configuration.


