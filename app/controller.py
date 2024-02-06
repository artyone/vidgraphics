import os

import numpy as np
import pandas as pd

from .model import get_data_from_file_1, get_data_from_file_2


class DataController:
    def __init__(self) -> None:
        self._data: None | pd.DataFrame = None
        self.filepath = None
        self._time_index = 0

    def get_all_data(self) -> pd.DataFrame | None:
        return self._data

    def get_data_main(self) -> pd.DataFrame | None:
        if self._data is None:
            return None
        return self._data.drop('data_vi', axis=1)

    def get_data_vi(self) -> pd.DataFrame | None:
        if self._data is None:
            return None
        data = self._data.iloc[self._time_index]['data_vi']
        time = np.arange(len(data))
        return pd.DataFrame({'time': time, 'data_vi': data})

    def get_headers_for_left_menu(self) -> list[tuple[str, int]] | None:
        if self._data is None:
            return None
        all_headers = list(self._data.columns)
        all_headers.remove('data_vi')
        all_headers.remove('time')
        all_headers = [(name, len(self._data[name])) for name in all_headers]
        return all_headers

    def set_fake_data(self) -> pd.DataFrame:
        # временные данные
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

    def read_data_from_file(self, filepath: str, num_func: str) -> None:
        self.filepath = filepath
        if num_func == '1':
            self._data = get_data_from_file_1(filepath)
        else:
            self._data = get_data_from_file_2(filepath)
        # self._data = self.get_fake_data()

    def read_data_from_dir(self, dirpath: str, num_func: str) -> None:
        self.filepath = dirpath
        data = []
        files = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
        for file in files:
            filepath = os.path.join(dirpath, file)
            try:
                if num_func == '1':
                    file_data = get_data_from_file_1(filepath)
                else:
                    file_data = get_data_from_file_2(filepath)
            except:
                continue
            else:
                data.append(file_data)
        self._data = pd.concat(data, ignore_index=True)
        if self._data is None:
            raise ValueError
        self._data['time'] = np.arange(0, len(self._data)*0.002, 0.002)

    def get_value_on_pos_x(self, pos_x=None):
        if self._data is None:
            return None
        time_col = self._data['time']
        if pos_x:
            self._time_index = (time_col - pos_x).abs().idxmin()
        return time_col.iloc[self._time_index]

    def set_next_time_index(self, backward=False, num=1) -> None:
        if self._data is None:
            raise ValueError
        if backward:
            self._time_index -= num
        else:
            self._time_index += num
        if self._time_index >= len(self._data):
            self._time_index = len(self._data) - 1
            raise StopIteration
        if self._time_index < 0:
            self._time_index = 0
            raise StopIteration


if __name__ == '__main__':
    ctrl = DataController()
    print(ctrl._data)
