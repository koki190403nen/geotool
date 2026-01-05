#!/usr/bin/env python3
# -*- cording: utf8 -*-
# SurfaceElevation.py: 河川堤防評価の「面評価」を実施するための関数
# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from osgeo import gdal
import geopandas as gpd
import glob, re
from tqdm import tqdm

# %%
#########
def surface_evaluation(liana_gdf, block_gdf, line_gdf, target_cols, max_distance, desc=None):
    """対象河川で面評価を実施するための関数
    Args:
        liana_gdf (gpd.GeoDataFrame, geometry: Point): LIANA観測結果の点群データ
        block_gdf (gpd.GeoDataFrame, geometry: Polygon): 分割ブロックの区画データ
        line_gdf (gpd.GeoDataFrame, geometry: LineStrings): 河川堤防中心線のラインデータ
        target_cols (list, str): 重み付き平均変動量を計算する対象となる列名（リスト）
        max_distance (int or float): 重みをつける際、考慮する距離
        desc (str): プログレスバーの先頭に表示する説明文字列

    Returns:
        _type_: _description_
    """
    out_gdf = block_gdf.copy()
    temporary_ls = []
    def calc_MeanVariableSpeed_by_block(block_items):
        liana_gdf_within_embankment = liana_gdf[liana_gdf.apply(lambda x: x.geometry.within(block_items.geometry), axis=1)]  # 堤防内の値を抽出
        distances = liana_gdf_within_embankment.apply(lambda x: x.geometry.distance(line_gdf.geometry), axis=1)  # LIANA観測点の堤防中心線からの距離
        weights   = ((max_distance - distances) / max_distance).values  # LIANA観測点の重み (5m-距離)/5m
        mean_variable_speed = np.nansum(weights*liana_gdf_within_embankment[target_cols], axis=0) / np.nansum(weights)  # 重み付き平均変動速度
        temporary_ls.append(mean_variable_speed)
    tqdm.pandas(desc=desc)
    out_gdf.progress_apply(func=calc_MeanVariableSpeed_by_block, axis=1)
    out_gdf[target_cols] = np.array(temporary_ls)
    return out_gdf

# %% 必要なデータの準備
if __name__=='__main__':
    river_name = '押川'
    # 1. lianaのデータ
    liana_gdf = gpd.GeoDataFrame(pd.concat([gpd.read_file(filepath) for filepath in glob.glob(f'L:/■2025/DC25T5019_茨城県_土・施　第２５９９０００００１ー１号　地球観測衛星を用いた河川堤防変動評価検討業務/05_業務実施/GISデータ/LIANA/gpkg/{river_name}*.gpkg')])).set_crs(epsg=6677)
    liana_gdf = liana_gdf[liana_gdf['信頼度(-1～-0,-1に近いほど計測精度の信頼性が高い)'].abs()>=0.98]
    # 2. 面ブロック
    block_gdf = gpd.read_file(f'L:/■2025/DC25T5019_茨城県_土・施　第２５９９０００００１ー１号　地球観測衛星を用いた河川堤防変動評価検討業務/05_業務実施/GISデータ/AOI/河川堤防範囲/ポリゴン/河川堤防バッファ_10m幅_分割済v2.geojson')
    block_gdf = block_gdf[block_gdf['河川名']==river_name]
    # 3. 堤防中心線
    line_gdf = gpd.read_file(f'L:/■2025/DC25T5019_茨城県_土・施　第２５９９０００００１ー１号　地球観測衛星を用いた河川堤防変動評価検討業務/05_業務実施/GISデータ/AOI/河川堤防範囲/ライン/河川堤防ライン.geojson')
    line_gdf = line_gdf.query(f'河川名=="{river_name}"').dissolve('河川名')
    # 4. 重み付き変動量を算出する対象の列一覧
    target_cols = [date for date in list(liana_gdf.columns) if re.search(r'\d+/\d+/\d+', date)]
    # 面評価の実施
    out_gdf = surface_evaluation(
        liana_gdf=liana_gdf,
        block_gdf=block_gdf,
        line_gdf=line_gdf,
        target_cols=target_cols,
        max_distance=5,
        desc=river_name
    )