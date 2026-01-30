#!/usr/bin/env python-3
# -*- coding: utf-8 -*-
# CheckSuperimposition.py: 同じ座標系の2つのベクタデータの重畳を確認する

# %%
import numpy as np
from osgeo import gdal
import geopandas as gpd
from ..Convert.vec2ras import vec2ras


# %%
from osgeo import ogr
def CheckSuperimposion(ori_vec_path, com_vec_path, ori_id,  out_attribute='Superimposition', resolution=10, ori_nodata=-9999):
    """同じ座標系の2つのベクターデータの重畳を確認する

    Args:
        ori_vec_path (_type_): 重畳有無を追加したいベクタ（オリジナルベクタ）
        compared_vec_path (_type_): 重なりを確認したいベクタ
        ori_id (_type_): オリジナルベクタのID属性名
        out_attribute (str, optional): 重畳有無を焼きこむ属性の値. Defaults to 'Superimposition'.
        resolution (int, optional): 解析解像度.単位は座標系を確認. Defaults to 10.
    """

    # オリジナルのベクタをラスタに変換
    ori_src = ogr.Open(ori_vec_path)
    com_src = ogr.Open(com_vec_path)
    ori_extent = ori_src.GetLayer().GetExtent()
    com_extent = com_src.GetLayer().GetExtent()
    del ori_src, com_src

    x_min = ori_extent[0] if ori_extent[0]<com_extent[0] else com_extent[0]
    x_max = ori_extent[1] if ori_extent[1]>com_extent[1] else com_extent[1]
    y_min = ori_extent[2] if ori_extent[2]<com_extent[2] else com_extent[2]
    y_max = ori_extent[3] if ori_extent[3]>com_extent[3] else com_extent[3]
    geotrans = (x_min, resolution, 0, y_max, 0, -1*resolution)
    cols = int((x_max - x_min) / resolution)
    rows = int((y_max - y_min) / resolution)

    ori_src = vec2ras(in_vector_path  = ori_vec_path, out_raster_path = './ori_working.tif', attribute=ori_id, geotrans = geotrans, cols=cols, rows=rows, nodata=-9999)
    vec2ras(in_vector_path  = com_vec_path, out_raster_path = './com_working.tif', geotrans = geotrans, cols=cols, rows=rows)
    ###### ラスタ化まで完了

    # ラスタの読み込み
    ori_img = gdal.Open(f'./ori_working.tif').ReadAsArray()
    com_img = gdal.Open(F'./com_working.tif').ReadAsArray()

    chojo_img_with_id = np.where((com_img==1)&(com_img!=ori_nodata), ori_img, np.nan).astype(np.float32)
    del ori_img, com_img
    
    # 重畳の確認 (np.unique使用)
    chojo_ids = np.unique(chojo_img_with_id.flatten())
    chojo_ids = list(chojo_ids[~np.isnan(chojo_ids)])

    # 属性に戻す
    out_gdf = gpd.read_file(ori_vec_path)
    out_gdf[out_attribute]=0
    target_idx = out_gdf.query(f'{ori_id} in {chojo_ids}').index
    out_gdf.loc[target_idx, out_attribute]=1

    return out_gdf
