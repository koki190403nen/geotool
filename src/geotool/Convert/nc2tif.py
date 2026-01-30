#!/usr/bin/env python3
# -*- cording:utf-8 -*-
# netCDF -> geotiff を行う

# %%
import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal
from netCDF4 import Dataset
from osgeo import gdal

# 自作ツール
from .base import Convert
from .arr2tif import arr2tif

# %%
class Nc2Tif(Convert):
    def __init__(self):
        super().__init__()
        self.in_extension='.nc'
        self.out_extension='.tif'
    
    # netCDF画像読込 -> self.img
    def in2arr(self, in_file_path):
        nc = Dataset(in_file_path)  # インスタンス化
        data_key = list(nc.variables.keys())[2]
        self.img = nc[data_key][:].data  # 実際のデータを入手する

        # 各種パラメータを計算
        self.dtype = self.img.dtype  # 実際のデータのdtype
        self.h, self.w = self.img.shape  # 実際のデータの高さと幅

        self.make_geotrans(nc)

    # arr -> geotif に変換する
    def arr2out(self, out_file_path):
        arr2tif(
            arr = self.img, out_file_path=out_file_path,
            geotrans=self.geotrans, dtype=gdal.GDT_Float32)

    
    # geotransを取得する
    def make_geotrans(self, nc):
        lat_arr = nc['latitude'][:].data
        lon_arr = nc['longitude'][:].data

        lat_accuracy = int(np.abs(np.round(np.log10(np.abs(lat_arr[1] - lat_arr[0]))))+2)
        lon_accuracy = int(np.abs(np.round(np.log10(np.abs(lon_arr[1] - lon_arr[0]))))+2)

        delta_lat = np.round(lat_arr[1] - lat_arr[0], lat_accuracy)
        delta_lon = np.round(lon_arr[1] - lon_arr[0], lon_accuracy)

        self.geotrans = (
            np.round(lon_arr[0] - delta_lon/2, lon_accuracy), delta_lon, 0,
            np.round(lat_arr[0] - delta_lat/2, lat_accuracy), 0, delta_lat
        )
        return self.geotrans

# %%
if __name__=='__main__':
    ng = NC2Tif()
    ng.save_out_multi('D:/ResearchData/Level1/himawari/', '../../sample/')