#!/usr/env python3
# -*- coding: utf-8 -*-
# vec2ras.py: ベクタをラスタに変換する

# %%
from osgeo import gdal, ogr, gdal_array
import numpy as np

def vec2ras(in_vector_path, out_raster_path, attribute=None, geotrans=None, cols=None, rows=None, resolution=None, nodata=-9999, dtype=np.int16):
    """ベクタをラスタ化

    Args:
        in_vector_path (str, path): 入力元ベクタのパス
        out_raster_path (str, path): 出力先ラスタのパス
        attribute (str, attribute): 焼きこむベクタの属性名
        geotrans (set, (x_min, resolution, 0, y_max, 0, -resolution)): 左上座標. Defaults to None. 指定しない場合ベクタ参照する
        cols(int): 列数
        rows(int): 行数
        resolution (int): 出力ラスタの解像度. Defaults to None.
        nodata (int, optional): nodataの出力値. Defaults to -9999.
        dtype (_type_, optional): 出力ラスタのデータタイプ. Defaults to np.int16.
    """

    # 出力元ベクタの読み込み
    src_ds = ogr.Open(in_vector_path)
    src_layer = src_ds.GetLayer()
    


    # geotransの設定
    if geotrans is None: # geotrans指定なしの場合は元のベクタを参照
        x_min, x_max, y_min, y_max = src_layer.GetExtent()
        cols = int((x_max - x_min) / resolution)
        rows = int((y_max - y_min) / resolution)
        geotrans = (x_min, resolution, 0, y_max, 0, -resolution)
    
    # 出力先geotiffの設定
    gdal_type = gdal_array.NumericTypeCodeToGDALTypeCode(dtype)
    target_ds = gdal.GetDriverByName('GTiff').Create(out_raster_path, cols, rows, 1, gdal_type)
    target_ds.SetGeoTransform(geotrans)

    # 座標系の設定
    projection = src_layer.GetSpatialRef().ExportToWkt()
    target_ds.SetProjection(projection)

    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(nodata)

    # ラスタ化
    if attribute is None:
        out_src = gdal.RasterizeLayer(target_ds, [1], src_layer, burn_values=[1])
    else:
        out_src = gdal.RasterizeLayer(target_ds, [1], src_layer, burn_values=[nodata], options=[f'ATTRIBUTE={attribute}'])
    del target_ds, src_ds
    return out_src