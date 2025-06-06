#!/usr/bin/env python-3
# -*- coding: utf-8 -*-
# RGB画像をHSI空間に飛ばす
import numpy as np
def RGB2HSI(img):
    """RGBをHSI空間に変換する

    Args:
        img (Array like, 3D): shape=(h,w,c)のimage.c=[R,G,B]
    """

    R,G,B = [img[:,:,i].astype(np.float32) for i in range(3)]

    # Hueの計算
    M = np.nanmax(img, axis=2)
    m = np.nanmin(img, axis=2)
    C = M-m
    H_dash = np.where(
        C==0, np.nan        , np.where(
        M==R, ((G-B)/C) % 6 , np.where(
        M==G, ((B-R)/C) + 2 , np.where(
        M==B, ((R-G)/C) + 4 , np.nan))))
    H = 60*H_dash

    # Intensityの計算
    I = (R+G+B)/3


    # Saturationの計算
    S = np.where(I==0, 0, (1-m/I))
    return np.array([H,S,I]).transpose([1,2,0]) 