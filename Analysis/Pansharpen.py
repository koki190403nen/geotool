#! usr/bin/env python-3
# -*- coding: utf-8 -*-
# Pansharpen.py: 衛星画像のパンシャープンツール

# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from osgeo import gdal
import geopandas as gpd
import cv2
from geotool.Convert import arr2tif

# %%
SPOT_MS_src = gdal.Open(F'L:/■2024/DS25T5005_金沢市_金沢市宅地造成及び特定盛土等規制法に基づく既存盛土等調査業務委託/05_業務実施/GISデータ/SPOT解析/衛星画像_解析用/SPOT_201509.tif')
SPOT_MS_img = SPOT_MS_src.ReadAsArray()

SPOT_PC_src = gdal.Open(F'L:/■2024/DS25T5005_金沢市_金沢市宅地造成及び特定盛土等規制法に基づく既存盛土等調査業務委託/05_業務実施/GISデータ/SPOT解析/衛星画像_パンクロ/SPOT_P_201509.tif')
SPOT_PC_img = SPOT_PC_src.ReadAsArray()

# %%
def transform_uint8_img(src_img, vmin=None, vmax=None):
    if vmin is None:
        vmin = np.nanmin(src_img.flatten())
    
    if vmax is None:
        vmax = np.nanmax(src_img.flatten())

    return ((src_img.astype(np.float32)-vmin) / (vmax-vmin)*255).astype(np.uint8)

def Pansharpen(MS_img, PC_img):
    """パンシャープン化ツール

    Args:
        MS_img (Array like: 2D(h,w)): マルチスペクトル画像
        PC_img (Array like: 3D(h,w,c)): パンクロ画像 

    Returns:
        Array like (3D): パンシャープン画像
    """
    out_h, out_w = PC_img.shape
    RGB_uint8_img = np.zeros([out_h, out_w, 3], dtype=np.uint8)
    for i in range(3):
        RGB_uint8_img[:,:,i] = transform_uint8_img(cv2.resize(MS_img[:,:,i], dsize=(out_w, out_h), interpolation=cv2.INTER_NEAREST))
    HSV_img = cv2.cvtColor(RGB_uint8_img, cv2.COLOR_RGB2HSV)
    HSV_img[:,:,2] = transform_uint8_img(src_img=PC_img)
    out_RGB_img = cv2.cvtColor(HSV_img, cv2.COLOR_HSV2RGB)
    return out_RGB_img