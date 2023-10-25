import pandas as pd
import numpy as np
from .model import get_data_from_file

class DataController:
    def __init__(self) -> None:
        self._data = None
        self.filepath = None
        self.time_index = None

    def get_data(self, on_time_index=False) -> pd.DataFrame:
        if self._data is None:
            return None
        if on_time_index:
            data = self._data.iloc[self.time_index]['data_vi']
            time = np.arange(len(data))
            return pd.DataFrame({'time':time, 'data_vi':data})
        return self._data.drop('data_vi', axis=1)
        
   
    def get_fake_data(self) -> pd.DataFrame:
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
            self.time_index = (time_col - pos_x).abs().idxmin()
        return time_col.iloc[self.time_index]

    

if __name__ == '__main__':
    ctrl = DataController()
    print(ctrl.data)