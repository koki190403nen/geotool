#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 複数のhdfファイルから一枚の合成画像を作成する (MOD14A2に適用可能)

# %%
import numpy as np
from osgeo import gdal
from .arr2tif import arr2tif
import rasterio
from rasterio.merge import merge
import os, glob


def MergeTrans(ori_paths, out_file_path, working_dir='./working/', resampleAlg='near'):
    """MOD14A2用 複数のファイルを合成していつものアフリカを作る

    Args:
        ori_paths (_type_): 入力hdfパスリスト
        out_file_path (_type_): 出力ファイルのパス
        working_dir (str, optional): workingディレクトリ. Defaults to './working/'.
    """
    os.makedirs(working_dir, exist_ok=True)
    for path in glob.glob(f'{working_dir}/*'):
        os.remove(path)
    

    tif_workings = []
    for hdf_path in ori_paths:
        hdf = gdal.Open(hdf_path)
        hdf_src = gdal.Open(hdf.GetSubDatasets()[0][0])
        area_code = hdf_path.split('.')[-4]

        ds = gdal.Warp(
            destNameOrDestDS=f'{working_dir}/{area_code}.tif',
            srcDSOrSrcDSTab=hdf_src,
            dstSRS='EPSG:4326',
            )

        tif_workings+=[f'{working_dir}/{area_code}.tif']

        del hdf, hdf_src, ds

    # ここで結合を行う
    src_files_to_mosaic = [rasterio.open(fp) for fp in tif_workings]

    mosaic, geotrans_io = merge(src_files_to_mosaic)

    fire_pixel = ((mosaic[0,:,:]>=7)&(mosaic[0,:,:]<=9)).astype(np.uint8)
    
    geotrans = (
        geotrans_io[2],geotrans_io[0],0,
        geotrans_io[5],0,geotrans_io[4]
    )
    arr2tif(fire_pixel, f'{working_dir}/merge.tif', geotrans=geotrans)
    del src_files_to_mosaic
    del mosaic, geotrans_io

    # 切り抜き
    output = gdal.Warp(
        destNameOrDestDS=f'{out_file_path}',
        srcDSOrSrcDSTab=f'{working_dir}/merge.tif',
        xRes=0.05, yRes=0.05,
        outputBounds=(-20,-40,55,40),
        resampleAlg=resampleAlg
    )
    del output
    
    for fp in glob.glob(f'{working_dir}/*.tif'):
        os.remove(fp)
    