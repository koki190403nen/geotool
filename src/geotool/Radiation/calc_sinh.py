#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# calc_sinh.py: 指定緯度経度の指定日時のsinhを計算する
# %%
import numpy as np
import datetime
import pandas as pd
# %%
def calc_sinh(lat, lon, date:pd.Timestamp, Ls=135):
    """sinhを計算する
        sinh = (sin lat)(sin delta) + (cos lat)(cos delta)(cos omega)

    Args:
        lat (float or np.ndarray): 緯度lattide(°)
        lon (float or np.ndarray): 経度longitude(°)
        date(datetime.datetime): 日時
        Ls (float): 標準子午線の経度(明石市の経度(°)) Defaults to 135.
    
    Return:
        sinh(float or np.ndarray): sinh
    """

    #############################
    dn = date.dayofyear  # DOY
    if (type(lat)==np.ndarray)&(type(date)==pd.DatetimeIndex):
        img_shape = lat.shape
        time_shape = len(date)
        lat, lon = np.array([lat]*time_shape).transpose(1,2,0), np.array([lon]*time_shape).transpose(1,2,0)
        JST = np.zeros((*img_shape, time_shape))
        JST[:,:] = date.hour + date.minute/60 + date.second/3600
        Gamma = np.zeros((*img_shape, time_shape))
        Gamma[:,:] = 2*np.pi*(dn - 1)/365  # ラジアン
        
    else:
        JST = date.hour + date.minute/60 + date.second/3600
        Gamma = 2*np.pi*(dn - 1)/365  # ラジアン

    # omegaの計算 ########################
    Et = (0.000075 + 0.001868*np.cos(Gamma) - 0.032077*np.sin(Gamma) - 0.014615*np.cos(2*Gamma) - 0.04089*np.sin(2*Gamma)) * 229.18  # 均時差(分)
    Hs =  JST + 4*(lon-Ls)/60 + Et/60  # 真太陽時(時)
    omega = np.where(Hs<12, 15*(Hs+12), 15*(Hs-12))
    # omegaここまで######################



    # delta(太陽赤緯)の計算##########
    delta = \
        (0.006918 - 0.399912*np.cos(Gamma) + 0.070257*np.sin(Gamma) \
        - 0.006758*np.cos(2*Gamma) + 0.000907*np.sin(2*Gamma) \
        - 0.002697*np.cos(3*Gamma) + 0.00148*np.sin(3*Gamma)) \
        * (180/np.pi)  # 太陽赤緯(°)
    

    sinh = np.sin(np.deg2rad(lat)) * np.sin(np.deg2rad(delta)) + np.cos(np.deg2rad(lat))*np.cos(np.deg2rad(delta))*np.cos(np.deg2rad(omega))
    return sinh

