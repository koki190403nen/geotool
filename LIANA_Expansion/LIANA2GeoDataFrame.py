#!/usr/bin/env python-3
# -*- cording: utf-8 -*-
# LIANA2GeoDataFrame.py: LIANA csvファイルをGeoDataFrame形式に変換するためのコード

# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import shapely

# %%
# csvデータの入力
def liana2geodataframe(ori_df, out_epsg=6677, coef=None, masking_polygon=None):
    """csv形式のlianaをNK用geojsonに変換するためのコード

    Args:
        ori_df (pandas.DataFrame): オリジナルの形式のDataFrame
        out_epsg (int): 出力先のEPSGコード. Defaults to 6677(日本測地系9系).
        coef (float): QGIS閲覧用画像の信頼度の閾値. Noneの場合はQGIS閲覧用画像を出力しない.
        masking_polygon (geopandas.GeoDataFrame): マスク用画像のGeoDataFrameデータ. Noneの場合はマスク後閲覧画像を出力しない.

    Returns:
        list(geopandas.GeoDataFrame): LIANAプロジェクト（全範囲・QGIS閲覧用・マスク後）のGeoDataFrame
    """
    out_df = ori_df.copy()
    out_df['geometry'] = shapely.points(ori_df['経度(deg)'], ori_df['緯度(deg)'])
    out_df['ID'] = np.arange(out_df.shape[0])

    out_vals=[]

    # 使うcolumnsの調整
    out_cols = ['ID']+list(ori_df.columns)[2:]
    out_df   = out_df[out_cols]
    out_gdf  = gpd.GeoDataFrame(out_df).set_crs(epsg=4326).to_crs(epsg=out_epsg)
    out_vals.append(out_gdf)
    if coef is not None:
        view_gdf = out_gdf[np.abs(out_gdf['信頼度(-1～-0,-1に近いほど計測精度の信頼性が高い)'])>=np.abs(coef)][['ID', '変動速度(cm/年,正:隆起,負:沈下)', 'geometry']]
        out_vals.append(view_gdf)
    if masking_polygon is not None:
        masked_gdf = out_gdf[out_gdf.within(masking_polygon.dissolve().loc[0,'geometry'])]
        out_vals.append(masked_gdf)

    

    return out_vals if out_vals.__len__()>=2 else out_vals[0]
