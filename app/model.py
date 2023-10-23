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
    result['data_vi'] = [arr[0:1024] for arr in result_array]
    result['at'] = np.concatenate(result_array[:, 1024:1025])
    result['kom_p'] = np.concatenate(result_array[:, 1025:1026])
    result['sharu_mean'] = np.concatenate(result_array[:, 1026:1027])
    result['sharu_dev'] = np.concatenate(result_array[:, 1027:1028])
    result['pto1_mean'] = np.concatenate(result_array[:, 1028:1029])
    result['pto1_dev'] = np.concatenate(result_array[:, 1029:1030])
    result['zad_strob_prm'] = np.concatenate(result_array[:, 1030:1031])
    result['md_zad'] = np.concatenate(result_array[:, 1031:1032])
    result['E_H_out'] = np.concatenate(result_array[:, 1032:1033])
    result['E_A_out'] = np.concatenate(result_array[:, 1033:1034])
    result['E_B_out'] = np.concatenate(result_array[:, 1034:1035])
    result['E_G_out'] = np.concatenate(result_array[:, 1035:1036])
    result['time'] = np.arange(len(result['data_vi']))

    return pd.DataFrame(result)


def unpack_data(packet_data):
    data = struct.unpack('>2x1024B12H82x', packet_data)
    return data



