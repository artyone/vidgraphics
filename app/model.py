import dpkt
import numpy as np
import pandas as pd



def get_data_from_file_2(filepath: str) -> pd.DataFrame:
    try:
        with open(filepath, 'rb') as f:
            pcap = dpkt.pcapng.Reader(f)
            bytes_list = [
                pkt for _, pkt in pcap if len(pkt) == 1174
            ]
    except:
        try:
            with open(filepath, 'rb') as f:
                pcap = dpkt.pcap.Reader(f)
                bytes_list = [
                    pkt for _, pkt in pcap if len(pkt) == 1174
                ]
        except:
            raise ValueError

    
    
    bytes_str = b''.join(bytes_list)

    dt = np.dtype([
        ('pack_header', np.uint8, 43),
        ('data_vi', np.uint8, 1024),
        ('null_bytes', np.uint8, 2),
        ('data_main', np.uint16, 12),
        ('null_bytes2', np.uint8, 81)
    ])
    dt = dt.newbyteorder('>')

    data = np.frombuffer(bytes_str, dtype=dt, count=-1)

    columns = [
        'kom_p', 'at', 'sharu_mean', 'sharu_dev', 'pto1_mean',
        'pto1_dev', 'zad_strob_prm', 'md_zad', 'E_H_out',
        'E_A_out', 'E_B_out', 'E_G_out'
    ]
    df = pd.DataFrame(data['data_main'], columns=columns, dtype=np.uint16)
    df['E_H_out'] = df['E_H_out'].astype(np.int16)
    df['E_A_out'] = df['E_A_out'].astype(np.int16)
    df['E_B_out'] = df['E_B_out'].astype(np.int16)
    df['E_G_out'] = df['E_G_out'].astype(np.int16)
    df['data_vi'] = list(data['data_vi'])
    df['time'] = np.arange(0, len(df)*0.002, 0.002)

    return df

def unpack_bits(columns, data):
    result = {}
    for i, name in enumerate(columns):
        result[name] = (data & (1 << i)) >> i
    return result

def get_data_from_file_1(filepath: str) -> pd.DataFrame:
    try:
        with open(filepath, 'rb') as f:
            pcap = dpkt.pcapng.Reader(f)
            bytes_list = [
                pkt for _, pkt in pcap if len(pkt) == 1274
            ]
    except:
        try:
            with open(filepath, 'rb') as f:
                pcap = dpkt.pcap.Reader(f)
                bytes_list = [
                    pkt for _, pkt in pcap if len(pkt) == 1274
                ]
        except:
            raise ValueError

    bytes_str = b''.join(bytes_list)

    dt = np.dtype([
        ('pack_header', np.uint8, 43),
        ('data_vi', np.uint8, 1024),
        ('null_bytes', np.uint8, 2),
        ('arinc_data', np.uint16, 9),
        ('bit_data', np.uint8, 9),
        ('null_bytes2', np.uint8, (1, )),
        ('data_main', np.int16, 41),
        ('null_bytes3', np.uint8, 58),
        ('time_src', np.uint32, (1, )), 
        ('null_bytes4', np.uint8, 33)
    ])
    dt = dt.newbyteorder('>')

    data = np.frombuffer(bytes_str, dtype=dt, count=-1)

    columns_main = [
        'MD', 'curr_27V', 'u_36V_C', 'u_36V_A', 'u_36V_B', 
        'u15V_p_AP', 'u15V_m_AP', 'u27V_del', 'alfa', 
        'u_5V', 'EA', 'EH', 'current', 'signal_D', 
        'Unn', 'Una', 'D_analog', 'gamma', 'epsilon', 
        'psi', 'ARU', 'E_H_ap', 'E_g', 'E_v', 'E_A_ap', 
        'u_12V', 'u_12V_gnd', 'u_12V_m_018A', 'u_12V_m_018A_gnd', 
        'u_48V', 'u_48V_gnd', 'u_8V', 'u_8V_gnd', 'u_6V_m_0075A', 
        'u_6V_m_gnd', 'u_12V_0075A', 'u_12V_0075A_gnd', 'u_6V', 
        'u_6V_gnd', 'u_6V_m_028A', 'u_6V_m_028A_gnd'
    ]

    columns_arinc = [
        'ARINC_081', 'ARINC_082', 'ARINC_083', 'ARINC_084', 
        'ARINC_085', 'ARINC_086', 'ARINC_087', 'ARINC_088', 
        'ARINC_089'	
    ]
    columns_bits = [
        [
            'send_ARINC', 'u27_p', 'u27_ground', 'u27_A', 'u27_A1', 'u36B_m', 'u36A_m', 'u15_m'
        ], 
        [
            'u15v_p', 'u36C_m', 'u15V_bk', 'off_vob', 'off_V', 'off_ASU', 'block_VP', 'off_CU'
        ], 
        [
            'vkl_rrch', 'PR_27v', 'block_AB', 'bridge27V', 'VPG_27V', 'komm_ASD', 'block_DP', 'sinhro'
        ], 
        [
            'RIP', 'D5', 'DVA1', 'DVA2', 'DVA3', 'DVA4', 'kom_vn', 'kontr_toka_rzp'
        ], 
        [
            'kontr_zahv_apch', 'kontr_vn', 'EhV', 'AV', 'PR_U505', 'Zg_27V', 'Kom_No', 'VK'
        ], 
        [
            'komm_PP', 'kom_mem_ASD', 'ASP', 'Tg_RAZI', 'MD_k', 'Tg_ZHO', 'ZH_ZH', 'Si_k'
        ],
        [
            'PPH', 'Sh_P2', 'izp_k', 'izr_k', 'strob_RZ', 'zona_1', 'zona_2', 'rpo'
        ], 
        [
            'AR', 'kom_rg_rv', 'sz', 'kom_ASD_k', 'Tg_ZH_Zh', 'kom_vp', 'null_1', 'null_2'
        ],
        [
            'kontrol_27V_m_pit', 'kontrol_27V_m', 'kontrol_27V_p_pit', 'kontrol_27V_p', 'kontrol_27V_p_A0', 'kontrol_27V_p_A1', 'kontrol_27V_p_A2', 'kontrol_27V_p_A3'
        ]
    ]

    df = pd.DataFrame(data['data_main'], columns=columns_main, dtype=np.int16)
    df['data_vi'] = list(data['data_vi'])
    df['time_src'] = data['time_src'] / 50_000
    for i, col in enumerate(columns_arinc):
        df[col] = data['arinc_data'][:,i].astype(np.uint16)
    
    for i, val in enumerate(columns_bits):
        res = unpack_bits(val, data['bit_data'][:, i])
        for key, value in res.items():
            df['z_' + key] = value.astype(np.bool_)

    df['time'] = np.arange(0, len(df)*0.002, 0.002)

    return df

