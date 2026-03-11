#!/usr/bin/env python3
# -*- coding: utf-8
# ftest.py: f検定を行う
import numpy as np
from scipy import stats

def Ftest(y1, y2):
    """F検定を行う
    帰無仮説：2つのサンプルの分散に差はない

    Args:
        y1 (Array like): サンプル1
        y2 (Array like): サンプル2

    Returns:
        f : F値
        p : p値
    """
    var1 = np.var(y1, ddof=1)
    var2 = np.var(y2, ddof=1)

    f = var2/var1
    dfn = len(y1) - 1
    dfd = len(y2) - 1
    f_cdf = stats.f.cdf(f, dfn=dfn, dfd=dfd)
    if f_cdf<0.5:
        p = f_cdf*2
    else:
        p = (1 - f_cdf)*2
    return f, p