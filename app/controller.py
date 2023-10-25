import numpy as np
import pandas as pd

from .model import get_data_from_file


class DataController:
    def __init__(self) -> None:
        self._data = None
        self.filepath = None
        self._time_index = None

    def get_all_data(self) -> pd.DataFrame:
        return self._data
    
    def get_data_main(self):
        if self._data is None:
            return None
        return self._data.drop('data_vi', axis=1)
    
    def get_data_vi(self):
        if self._time_index is None or self._data is None:
            return None
        data = self._data.iloc[self._time_index]['data_vi']
        time = np.arange(len(data))
        return pd.DataFrame({'time':time, 'data_vi':data})
    
    def get_headers_for_left_menu(self):
        if self._data is None:
            return None
        all_headers = list(self._data.columns)
        all_headers.remove('data_vi')
        all_headers.remove('time')
        all_headers = [(name, len(self._data[name])) for name in all_headers]
        return all_headers
   
    def set_fake_data(self) -> pd.DataFrame:
        #временные данные
        time = np.arange(0, 10, 0.1)
        sin_values = np.sin(time)
        data_vi = [np.random.rand(25) for _ in time]
        df = pd.DataFrame(
            {
                'time': time, 
                'sin': sin_values, 
                'data_vi': data_vi
            })
        return df
    
    def read_data_from_file(self, filepath: str) -> pd.DataFrame:
        self.filepath = filepath
        self._data = get_data_from_file(filepath)
        #self._data = self.get_fake_data()

    def get_value_on_pos_x(self, pos_x=None):
        time_col = self._data['time']
        if pos_x:
            self._time_index = (time_col - pos_x).abs().idxmin()
        return time_col.iloc[self._time_index]

    def update_time_index(self):
        if self._time_index is None:
            self._time_index = 0
        self._time_index += 1
    

if __name__ == '__main__':
    ctrl = DataController()
    print(ctrl._data)