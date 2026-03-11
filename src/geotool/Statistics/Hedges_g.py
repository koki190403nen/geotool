#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Hedge's gを求める
import numpy as np
def Hedges_g(x1, x2):
    """Hedge's gの効果量を算出する

    Args:
        x1 (Array Like): 比較したい郡1
        x2 (Array Like): 比較したい郡2

    Returns:
        g: Hedge's g 効果量
        (-ci, +ci): 95%信頼区間
        SD: 標準誤差
    """
    n1, n2 = len(x1), len(x2)
    x1_mean, x2_mean = np.nanmean(x1), np.nanmean(x2)
    s1, s2 = np.nanstd(x1), np.nanstd(x2)

    s = np.sqrt(((n1-1) * s1**2 + (n2-1) * s2**2) / (n1+n2-2))

    g = np.abs(x1_mean-x2_mean) / s

    SD = np.sqrt((n1+n2)/(n1*n2) + g**2 / (2*(n1+n2-3)))

    ci = (g-1.96*SD, g+1.96*SD)

    return g, ci