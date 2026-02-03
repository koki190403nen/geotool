#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#SizeFilter.py: 一定面積以上のピクセル群のみを抽出する
# %%
import cv2
import numpy as np
def SizeFilter(img, lower_size, upper_size=np.inf):
    """一定面積以上のピクセル群のみを抽出する

    Args:
        img (Array like): 2次元画像(numpy array)。バイナリ形式
        lower_size (int): lower_size以上のピクセル数が固まっている群を抽出する
        upper_size (float): upper_size以下のピクセル数が固まっている群を抽出する. Defaults: np.inf（上限なし）
    
    Returns:
        Array like, 2D: 一定以上の面積のピクセル群
    """

    img = img.astype(np.uint8)
    id_size, labeled_img = cv2.connectedComponents(img)
    id_arr, area_arr = np.unique(labeled_img, return_counts=True)
    area_img = area_arr[labeled_img]
    out_img = np.where(
        (area_img!=np.nanmax(area_arr))&(area_img>=lower_size)&(area_img<=upper_size),
        1, 0
        )
    return out_img