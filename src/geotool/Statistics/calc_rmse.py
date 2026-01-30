#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RMSEを算出する関数
# %%
import numpy as np
def calc_rmse(obs, pred, percentage=True):
    """RMSEを算出する

    Args:
        obs  (Array Like): 観測値
        pred (Array Like): 推定値
        percentage (bool): 観測値で正規化し、%にするかどうか. Defaults to True.

    """
    if percentage:
        return np.sqrt(np.nanmean((obs-pred)**2)) / np.nanmean(obs)
    else:
        return np.sqrt(np.nanmean((obs-pred)**2))