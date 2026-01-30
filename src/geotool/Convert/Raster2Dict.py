#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# raster2dict_mR95pT_NDVI.py: RAWデータから指定した座標値のmR95pTとNDVIを抜き出して書き出す

# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime
import json

# %%
class Raster2Dict:
    def __init__(self, lat, lon, area_name):
        """指定した座標のデータをcsvにまとめる

        Args:
            lat (float): 指定したい緯度
            lon (float): 指定したい経度
            area_name (str): 地点名
        """
        self.lat=lat
        self.lon=lon

        # メタデータの保存
        self.meta_csv_path = 'C:/Users/koki1/Google ドライブ/develop/ForReseach/sample/dataset/meta.csv'
        try:
            self.meta_df = pd.read_csv(self.meta_csv_path)
        except(FileNotFoundError):
            self.meta_df = pd.DataFrame()


        self.meta_df.loc[area_name, 'lat'] = lat
        self.meta_df.loc[area_name, 'lon'] = lon
        self.meta_df.to_csv(self.meta_csv_path)

        self.h, self.w  = 1600, 1500
        self._convert_row_col()  # lat_lon -> row_col


        # データ本体の記録のための前処理
        self.date_arr = pd.to_datetime(
            [f'{year}/{doy}' for year in range(2001, 2020+1) for doy in range(1, 366, 16)],
            format="%Y/%j"
        )
        self.dataset_df     = pd.DataFrame(index=self.date_arr)

    def capture(self):

        # mR95pTの取得
        self.get_index(
            key     = 'mR95pT',
            dir     = 'D:/ResearchData3/Level4/MOD16days/CCIs/mR95pT/',
            dtype   = 'float64'
            )
        
        # SPI3の取得
        self.get_index(
            key     = 'SPI3',
            dir     = 'D:/ResearchData3/Level4/MOD16days/SPI3/',
            dtype   = 'float32'
        )

        # DayLSTZの取得
        self.get_index(
            key     = 'DayZ',
            dir     = 'D:/ResearchData3/Level4/MOD16days/LST/DayZ/',
            dtype   = 'float32',
        )

        # VZIの取得
        self.get_index(
            key     = 'VZI',
            dir     = 'D:/ResearchData3/Level4/MOD16days/VZI/',
            dtype   = 'float32'
        )

        # DayLSTの取得
        self.get_index(
            key     = 'DayLST',
            dir     = 'D:/ResearchData3/Level3/MOD11C4/DayLST/',
            dtype   = 'float32'
        )

        # MaxTEMPの取得
        self.get_index(
            key     = 'MaxTemp',
            dir     = 'D:/ResearchData3/Level3/CPCTemp/MaxTEMP/',
            dtype   = 'float32'
        )

        # NDVIの取得
        self.get_index(
            key     = 'MOD13C1',
            dir     = 'D:/ResearchData3/Level3/MOD13C1/',
            dtype   = 'int16'
        )
    
        return self.dataset_df




    def get_index(self, key, dir, dtype):
        """指定したインデックスを取得し、self.dataset_dfにまとめる

        Args:
            key (str): インデックス名
            dir (str (path)): 保存先ディレクトリのパス
            dtype (str): データのdtype

        Returns:
            _type_: _description_
        """
        print(f'Getting {key} has initialized...')
        all_img_arr = np.zeros((self.h, self.w, len(self.date_arr)), dtype=np.float32)
        for c, date in enumerate(self.date_arr):
            get_img = np.fromfile(
                f'{dir}/{key}.A{date.strftime("%Y%j")}.{dtype}_h1600w1500.raw',
                count=self.h * self.w, dtype=dtype
            ).reshape(self.h, self.w).astype(np.float32)
            all_img_arr[:,:,c] = get_img
        
        self.dataset_df[key] = all_img_arr[self.row, self.col, :]
        return self.dataset_df

    def _convert_row_col(self):
        self.row, self.col = int((self.lat - 40) / (-0.05)), int((self.lon - (-20)) / (0.05))
        return self.row, self.col

# %%
if __name__=='__main__':
    r2d = Raster2Dict(-17.215, 27.424, 'Zambia2')
    r2d.capture()
    r2d.dataset_df.to_csv('../../sample/dataset/Zambia2.csv')

# %%
