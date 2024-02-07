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
    coef_main = [ 
        0.01, 1, 1, 1, 1, 
        1, 1, 1, 1, 1, 
        0.00244, 0.00244, 1, 0.00488, 1, 
        1, 0.00488, 0.00244, 0.00244, 0.00244, 
        1, 0.1, 1, 1, 0.1, 
        1, 1, 1, 1, 1, 
        1, 1, 1, 1, 1, 
        1, 1, 1, 1, 1, 
        1, 
    ]

    columns_arinc = [
        'ARINC_081', 'ARINC_082', 'ARINC_083', 'ARINC_084', 
        'ARINC_085', 'ARINC_086', 'ARINC_087', 'ARINC_088', 
        'ARINC_089'	
    ]
    columns_bits = [
        [
            'z_send_ARINC', 'z_u27_p', 'z_u27_ground', 'z_u27_A', 'z_u27_A1', 'z_u36B_m', 'z_u36A_m', 'z_u15_m'
        ], 
        [
            'z_u15v_p', 'z_u36C_m', 'z_u15V_bk', 'z_off_vob', 'z_off_V', 'z_off_ASU', 'z_block_VP', 'z_off_CU'
        ], 
        [
            'z_vkl_rrch', 'z_PR_27v', 'z_block_AB', 'z_bridge27V', 'z_VPG_27V', 'z_komm_ASD', 'z_block_DP', 'z_sinhro'
        ], 
        [
            'z_RIP', 'z_D5', 'z_DVA1', 'z_DVA2', 'z_DVA3', 'z_DVA4', 'z_kom_vn', 'z_kontr_toka_rzp'
        ], 
        [
            'z_kontr_zahv_apch', 'z_kontr_vn', 'z_EhV', 'z_AV', 'z_PR_U505', 'z_Zg_27V', 'z_Kom_No', 'z_VK'
        ], 
        [
            'z_komm_PP', 'z_kom_mem_ASD', 'z_ASP', 'z_Tg_RAZI', 'z_MD_k', 'z_Tg_ZHO', 'z_ZH_ZH', 'z_Si_k'
        ],
        [
            'z_PPH', 'z_Sh_P2', 'z_izp_k', 'z_izr_k', 'z_strob_RZ', 'z_zona_1', 'z_zona_2', 'z_rpo'
        ], 
        [
            'z_AR', 'z_kom_rg_rv', 'z_sz', 'z_kom_ASD_k', 'z_Tg_ZH_Zh', 'z_kom_vp', 'z_null_1', 'z_null_2'
        ],
        [
            'z_kontrol_27V_m_pit', 'z_kontrol_27V_m', 'z_kontrol_27V_p_pit', 'z_kontrol_27V_p', 'z_kontrol_27V_p_A0', 'z_kontrol_27V_p_A1', 'z_kontrol_27V_p_A2', 'kontrol_27V_p_A3'
        ]
    ]

    df = pd.DataFrame(data['data_main'], columns=columns_main, dtype=np.int16)
    for names, coef in zip(columns_main, coef_main):
        df[names] = df[names] * coef
    df['data_vi'] = list(data['data_vi'])
    df['time_src'] = data['time_src'] / 50_000
    for i, col in enumerate(columns_arinc):
        df[col] = data['arinc_data'][:,i].astype(np.uint16)
    
    for i, names in enumerate(columns_bits):
        res = unpack_bits(names, data['bit_data'][:, i])
        bits_df = pd.DataFrame(data=res)
        df = df.join(bits_df)
        # for key, value in res.items():
        #     df['z_' + key] = value

    df['time'] = np.arange(0, len(df)*0.002, 0.002)

    return df

