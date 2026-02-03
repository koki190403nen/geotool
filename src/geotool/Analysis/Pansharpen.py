#! usr/bin/env python-3
# -*- coding: utf-8 -*-
# Pansharpen.py: 衛星画像のパンシャープンツール

# %%
import numpy as np
import cv2

# %%
def transform_uint8_img(src_img, vmin=None, vmax=None):
    """8bit以上の画像を8bit画像に変換する関数

    Args:
        src_img (Array like, 2D): 8bit より大きい画像。1ch
        vmin (float): 画素値の上限（色調調整用） Defaults to None.
        vmax (float): 画素値の上限（色調調整用） Defaults to None.

    Returns:
        Array like, 2D: 8bit画像. 1ch
    """
    if vmin is None:
        vmin = np.nanmin(src_img.flatten())
    
    if vmax is None:
        vmax = np.nanmax(src_img.flatten())

    return ((src_img.astype(np.float32)-vmin) / (vmax-vmin)*255).astype(np.uint8)

def pansharpened(MS_img, PC_img):
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