from scapy.all import rdpcap
import struct
import numpy as np
import pandas as pd

def get_data_from_file(filepath):
    packets = rdpcap(filepath)
    result = {
        'data_vi': [],
        'at': [],
        'kom_p': [],
        'sharu_mean': [],
        'sharu_dev': [],
        'pto1_mean': [],
        'pto1_dev': [],
        'zad_strob_prm': [],
        'md_zad': [],
        'E_H_out': [],
        'E_A_out': [],
        'E_B_out': [],
        'E_G_out': [],
    }
    result_array = []
    # Распаковка данных из пакетов
    for packet in packets:
        try:
            unpacked_data = unpack_data(bytes(packet['Raw'].load))
            result_array.append(unpacked_data)
        except struct.error as e:
            print("Ошибка при распаковке данных пакета:", e)

    result_array = np.array(result_array)
    # result['data_vi'] = result_array[:, 0:512]
    result['at'] = result_array[:, 512:513]
    result['kom_p'] = result_array[:, 513:514]
    result['sharu_mean'] = result_array[:, 514:515]
    result['sharu_dev'] = result_array[:, 515:516]
    result['pto1_mean'] = result_array[:, 516:517]
    result['zad_strob_prm'] = result_array[:, 517:518]
    result['md_zad'] = result_array[:, 518:519]
    result['E_H_out'] = result_array[:, 519:520]
    result['E_A_out'] = result_array[:, 520:521]
    result['E_B_out'] = result_array[:, 521:522]
    result['E_G_out'] = result_array[:, 522:523]

    return pd.DataFrame(result)


def unpack_data(packet_data):
    data = struct.unpack('>566H', packet_data)
    return data



