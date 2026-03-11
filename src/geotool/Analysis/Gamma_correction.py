#! usr/bin/env python-3
# -*- coding: utf-8 -*-
# Gamma_correction.py: ガンマ補正を行う
import numpy as np

def gamma_correction(src, gamma=1):
    """ガンマ補正を行う関数

    Args:
        src (Array like, 3D): ガンマ補正を行う画像 (dtype:uint8)
        gamma (float, 0~1): ガンマ値. Defaults to 1.

    Returns:
        Array like, 3D: ガンマ補正後の画像(dtype: uint8)
    """
    return (((src.astype(np.float32) / 255) ** (1/gamma)) * 255).astype(np.uint8)