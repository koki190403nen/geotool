#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tiling_satellite_img.py: 衛星画像をタイル化する関数
# %%
import numpy as np
from osgeo import gdal
from .arr2tif import arr2tif
import os

# %%
def tiling_satellite_img_3band(src_path, dst_path, band_ls = [0, 1, 2], vmins=[None, None, None], vmaxes=[None, None,None], log=False):
    """画像をuint8に変換するコード(3band)

    Args:
        src_path (str: path): 変換元の画像のパス
        dst_path (str: path): タイルデータの保存先のパス
        band_ls (list: int): RGBのバンドのリスト
        vmins (list: float) : 下限値(色調調整用)のリスト (R G Bの順)
        vmaxes (list: float): 上限値(色調調整用)のリスト (R G Bの順)
        log (bool): ログの出力の有無. Default's False
    """
    os.makedirs('./working/', exist_ok=True)
    # === 画像のuint8への正規化 ===
    src = gdal.Open(src_path)
    src_img = src.ReadAsArray().transpose((1,2,0))

    # === 画像の正規化の実施 ===
    if log:
        print('(1/4)画像の正規化')
    if src_img.dtype==np.uint8:  # dtypeが8ビットならば変換の必要なし
        out_img = src_img
        tileformat = 'PNG'  if out_img.shape[2] else 'JPEG'
    else:  # 8ビット以外ならば8ビットに変換する
        h,w,c = src_img.shape
        tileformat = 'JPEG'
        out_img = np.zeros((h,w,3)).astype(np.uint8)  # 8ビットの入れ子を作る
        for band, vmin, vmax in zip(band_ls, vmins, vmaxes):
            target_band_img = src_img[:,:,band]
            if vmin is None:  # vminが記載なしならば2%tile値を下限とする
                vmin = np.percentile(target_band_img[~np.isnan(target_band_img)], 2)
            if vmax is None:  # vmaxが記載なしならば98%tile値を上限とする
                vmax = np.percentile(target_band_img[~np.isnan(target_band_img)], 98)
            out_img[:,:,band] = ((target_band_img - vmin) / (vmax - vmin) * 255).astype(np.uint8)

    # === 正規化画像を一度出力する ===
    arr2tif(
        out_img,
        out_file_path='./working/working1.tif',
        geotrans = src.GetGeoTransform(),
        projection = src.GetProjection()
    )

    # === epsg3857に変換する ===
    if log:
        print('(2/4) epsg:3857に再投影')
    warp_ds = gdal.Warp(
        destNameOrDestDS = './working/working2.tif',
        srcDSOrSrcDSTab  = './working/working1.tif',
        dstSRS = 'EPSG:3857',
        resampleAlg='near',
        multithread=True
    )
    warp_ds = None

    # === GPKGに変換する ===
    if log:
        print('(3/4) GPKGへの変換')
    gdal.Translate(
        destName    = dst_path,
        srcDS       = './working/working2.tif',
        format      = 'GPKG',
        creationOptions = [
            f'TILE_FORMAT={tileformat}',
        ]
    )

    # === ズームレベルを設定する ===
    if log:
        print('(4/4)ズームレベルの設定')
    ds = gdal.Open(dst_path, gdal.GA_Update)
    ds.BuildOverviews(overviewlist=[2,4,8,16,32], resampling='NEAREST')
    ds = None
    print('完了')

# %%
if __name__=="__main__":
    # 実験
    tiling_satellite_img_3band(
        src_path = 'L:/■2025/DP26T5001_静岡県_令和７年度静岡県衛星画像を活用した盛土監視体制強化業務委託/05_業務実施/GIS/衛星画像/PlanetScope衛星画像/R7_1時期目/20250321_shizuoka.tif',
        dst_path = 'tile.gpkg',
        band_ls=[0, 1, 2],
        #vmins  = [0, 0, 0],
        #vmaxes = [255, 255, 255],
        log = True
    )
# %%
def tiling_satellite_img_1band(src_path, dst_path, vmin=None, vmaxes=None, log=False):
    """画像をuint8に変換するコード(1band)

    Args:
        src_path (str: path): 変換元の画像のパス
        dst_path (str: path): タイルデータの保存先のパス
        vmin (float): 下限値(色調調整用)
        vmax (float): 上限値(色調調整用)
        log (bool): ログの出力の有無. Default's False
    """
    os.makedirs('./working/', exist_ok=True)
    # === 画像のuint8への正規化 ===
    src = gdal.Open(src_path)
    src_img = src.ReadAsArray().transpose((1,2,0))

    # === 画像の正規化の実施 ===
    if log:
        print('(1/4)画像の正規化')
    if src_img.dtype==np.uint8:  # dtypeが8ビットならば変換の必要なし
        out_img = src_img
        tileformat = 'PNG'  if out_img.shape[2] else 'JPEG'
    else:  # 8ビット以外ならば8ビットに変換する
        h,w,c = src_img.shape
        tileformat = 'JPEG'
        out_img = np.zeros((h,w,3)).astype(np.uint8)  # 8ビットの入れ子を作る
        for band, vmin, vmax in zip(band_ls, vmins, vmaxes):
            target_band_img = src_img[:,:,band]
            if vmin is None:  # vminが記載なしならば2%tile値を下限とする
                vmin = np.percentile(target_band_img[~np.isnan(target_band_img)], 2)
            if vmax is None:  # vmaxが記載なしならば98%tile値を上限とする
                vmax = np.percentile(target_band_img[~np.isnan(target_band_img)], 98)
            out_img[:,:,band] = ((target_band_img - vmin) / (vmax - vmin) * 255).astype(np.uint8)

    # === 正規化画像を一度出力する ===
    arr2tif(
        out_img,
        out_file_path='./working/working1.tif',
        geotrans = src.GetGeoTransform(),
        projection = src.GetProjection()
    )

    # === epsg3857に変換する ===
    if log:
        print('(2/4) epsg:3857に再投影')
    warp_ds = gdal.Warp(
        destNameOrDestDS = './working/working2.tif',
        srcDSOrSrcDSTab  = './working/working1.tif',
        dstSRS = 'EPSG:3857',
        resampleAlg='near',
        multithread=True
    )
    warp_ds = None

    # === GPKGに変換する ===
    if log:
        print('(3/4) GPKGへの変換')
    gdal.Translate(
        destName    = dst_path,
        srcDS       = './working/working2.tif',
        format      = 'GPKG',
        creationOptions = [
            f'TILE_FORMAT={tileformat}',
        ]
    )

    # === ズームレベルを設定する ===
    if log:
        print('(4/4)ズームレベルの設定')
    ds = gdal.Open(dst_path, gdal.GA_Update)
    ds.BuildOverviews(overviewlist=[2,4,8,16,32], resampling='NEAREST')
    ds = None
    print('完了')