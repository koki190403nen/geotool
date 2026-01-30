#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# calc_zscore.py: 元時系列データから季節性を考慮したZスコアを算出する
# %%
import numpy as np

def calc_zscore(arr, period):
    arr_2d = arr.reshape(-1, period)
    years  = arr_2d.shape[0]

    arr_mean = np.array(list(np.nanmean(arr_2d, axis=0))*years)
    arr_std  = np.array(list(np.nanstd (arr_2d, axis=0))*years)

    z_score = (arr - arr_mean) / arr_std
    return z_score