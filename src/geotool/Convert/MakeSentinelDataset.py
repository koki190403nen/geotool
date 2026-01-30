#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MakeSentinelDataset.py: SAFE.zip形式のsentinel-2データからバンド情報を抽出する

# %%
import os, glob, shutil
import numpy as np
import pandas as pd


def MakeSentinelDataset(ori_zip_path, out_dir, use_bands=[2,3,4,8], resolution=10, work_dir='./working/'):
    """SAFE.zip形式のsentinel-2データからバンド情報を抽出する

    Args:
        ori_zip_path (str, path): 入力zipファイルパス
        out_dir (str, path): 出力先のディレクトリパス
        use_bands (list, optional): 出力したいバンド名. Defaults to [2,3,4,8].
        resolution (int): 対象の空間解像度[m]
        work_dir (str, path): ファイル解凍用の一時ディレクトリ. Defaults to './working/'.

    Returns:
        _type_: _description_
    """
    ##
    # 日付を取得する
    date_str = os.path.basename(ori_zip_path).split('_')[2]
    date = pd.to_datetime(date_str, format='%Y%m%dT%H%M%S')

    # 衛星名を取得する
    satellite = os.path.basename(ori_zip_path).split('_')[0]

    ## ワーキングディレクトリの作成
    shutil.rmtree(work_dir) if os.path.isdir(work_dir) else None  # 念のため削除
    os.makedirs(work_dir, exist_ok=True)

    ## 出力ディレクトリの作成
    out_product_dir = f'{out_dir}//{satellite}_{date.strftime("%Y%m%dT%H%M%S")}//'
    os.makedirs(out_product_dir, exist_ok=True)

    shutil.unpack_archive(ori_zip_path, work_dir)  # zipのアンパック
    ori_band_dir = glob.glob(f'{work_dir}/*/GRANULE/*/IMG_DATA/R{resolution}m')[0]  # オリジナルのバンドが格納されたディレクトリパス

    # バンドごとにターゲットディレクトリに保管していく
    for band in use_bands:
        band_file_path = glob.glob(f'{ori_band_dir}/*B{str(band).zfill(2)}*.jp2')[0]  # 元のバンドデータのパスの取得
        out_file_path  = f'{out_product_dir}/B{str(band).zfill(2)}.jp2'
        shutil.copy(band_file_path, out_file_path)

    # 雲被覆バンドを移動
    cld_file_path = glob.glob(f"{work_dir}//*//GRANULE//*//QI_DATA//MSK_CLDPRB_20m.jp2")[0]
    shutil.copy(cld_file_path, f'{out_product_dir}//CLDPRB.jp2')
    
    snw_file_path = glob.glob(f"{work_dir}//*//GRANULE//*//QI_DATA//MSK_SNWPRB_20m.jp2")[0]
    shutil.copy(snw_file_path, f'{out_product_dir}//SNWPRB.jp2')

    shutil.rmtree(work_dir)
    return out_product_dir