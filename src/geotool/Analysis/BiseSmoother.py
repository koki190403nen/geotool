#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# BiseSmoother.py: BISE法でスムージングを行う
#%%
import numpy as np
import pandas as pd

def bise_smoother(x, over_diff_size):
    before_diff = np.concatenate([np.array([0]), np.diff(x)])  # 前のデータとの差分
    after_diff = -1*np.concatenate([np.diff(x), np.array([0])])  # 後のデータとの差分

    # Null埋め
    if np.sign(over_diff_size)==-1:
        null_padding_arr = np.where(
            (before_diff<= over_diff_size)&(after_diff<=over_diff_size),
            np.nan,
            x
        )
    elif np.sign(over_diff_size)==1:
        null_padding_arr = np.where(
            (before_diff>= over_diff_size)&(after_diff>=over_diff_size),
            np.nan,
            x
        )

    # 線形補間
    smoothed_arr = pd.Series(null_padding_arr).interpolate(method='linear').values

    return smoothed_arr