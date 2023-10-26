import dpkt
import numpy as np
import pandas as pd


def get_data_from_file(filepath):
    with open(filepath, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        bytes_list = [
            pkt for _, pkt in pcap if len(pkt) == 1174
        ]

    bytes_str = b''.join(bytes_list)

    custom_dtype = np.dtype([
        ('pack_header', np.uint8, 42),
        ('null_bytes', np.uint8, 2),
        ('data_vi', np.uint8, 1024),
        ('data_main', np.uint16, 12),
        ('null_bytes2', np.uint8, 82)
    ])

    data = np.frombuffer(bytes_str, dtype=custom_dtype, count=-1)

    columns = [
        'at', 'kom_p', 'sharu_mean', 'sharu_dev', 'pto1_mean',
        'pto1_dev', 'zad_strob_prm', 'md_zad', 'E_H_out',
        'E_A_out', 'E_B_out', 'E_G_out'
    ]
    df = pd.DataFrame(data['data_main'], columns=columns, dtype=np.uint16)
    df['data_vi'] = list(data['data_vi'])
    df['time'] = np.arange(0, len(df)*0.002, 0.002)

    return df