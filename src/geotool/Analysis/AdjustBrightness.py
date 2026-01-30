#!/usr/bin/env python-3
# -*- coding utf-8 -*-
# adjust_brightness.py: 輝度調整のための関数

import numpy as np
from matplotlib import pyplot as plt


def add_sub_void_overflow(src, dif):
    """オーバーフローを考慮した加減計算

    Args:
        src (Array like:np.uint8): 加減される値
        dif (int): 加減する値

    Returns:
        Array like:np.uint8: 加減後の値
    """
    if src.dtype != np.uint8:
        raise TypeError
    sign = np.sign(dif)
    dst  = (src + dif).astype(np.uint8)
    out_val = np.where(
        (sign==1) &(src>dst), 255,np.where(
        (sign==-1)&(src<dst), 0, dst
        )
    ).astype(src.dtype)
    return out_val

def adjust_brightness(src, brightness):
    """輝度の調整

    Args:
        src (Array like: np.uint8): 輝度調整前画像
        brightness (int): 輝度調整量

    Returns:
        Array like: 輝度調整後画像
    """
    return add_sub_void_overflow(src, brightness)
