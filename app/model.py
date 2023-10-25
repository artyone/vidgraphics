from scapy.utils import PcapReader
from scapy.all import Raw
import struct
import numpy as np
import pandas as pd

def unpack_data(packet_data):
    format_string = '>2x1024B12H82x'
    data = struct.unpack(format_string, packet_data)
    return data


def get_data_from_file(filepath):
    packets = PcapReader(filepath)

    unpacked_array = []
    for packet in packets:
        try:
            unpacked_array.append(unpack_data(packet[Raw].load))
        except struct.error as e:
            print("Ошибка при распаковке данных пакета:", e)

    unpacked_array = np.array(unpacked_array)

    data_vi = list(np.array(unpacked_array[:, :1024], dtype=np.uint8))
    main_data = np.array(unpacked_array[:, 1024:], dtype=np.uint16)
    
    columns = [
        'at', 'kom_p', 'sharu_mean', 'sharu_dev', 'pto1_mean',
        'pto1_dev', 'zad_strob_prm', 'md_zad', 'E_H_out', 
        'E_A_out', 'E_B_out', 'E_G_out'
    ]
    df = pd.DataFrame(
        main_data, columns=columns, dtype=np.uint16)
    df['data_vi'] = data_vi
    df['time'] = np.arange(len(df))

    return df




