#!/usr/bin/env python-3
# -*- coding: utf-8 -*-
# SPI_3.py: SPI-3を求める

# %%
# SPIを計算する
import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import pyplot as plt

# %%
# SPI-3を求める
class SPI_3:
    def __init__(self, target_PRCPTOT, in_date_arr):
        """SPI-3を求める

        Args:
            target_PRCPTOT (Array like): ある一点のPRCPTOT
            in_date_arr (pandas.TimeStamp): 使用するデータの時間ラベル
        """
        self.target_PRCPTOT = target_PRCPTOT
        self.sorted_PRCPTOT = None

        self.in_date_arr = in_date_arr
        self.sorted_date_arr = None

        self.gamma_params = {}
        self.gamma_available = {}
        self.SPI_arr = None

    def fit(self):
        for month in range(1, 12+1):
            self.make_conv_dataset().calc_gamma_params(month)
        
        SPI_ls = []
        for PRCPTOT, month in zip(self.sorted_PRCPTOT, self.sorted_date_arr.month):
            SPI = self.calc_spi(PRCPTOT, month)
            SPI_ls.append(SPI)
        self.SPI_arr = np.array(SPI_ls)
        
        return self
    
    def calc_gamma_params(self, out_month):
        """ガンマ分布のパラメータを計算する

        Args:
            out_month (int): パラメータを求めたい月
        """
        using_PRCPTOT = self.sorted_PRCPTOT[self.sorted_date_arr.month==out_month]
        if np.nansum(using_PRCPTOT>0)<30:
            self.gamma_available[out_month] = False
        else:
            self.gamma_available[out_month] = True
            self.gamma_params[out_month] = stats.gamma.fit(using_PRCPTOT)
        return self
    
    def calc_spi(self, PRCPTOT, month):
        if self.gamma_available[month]:
            cdf = stats.gamma.cdf(PRCPTOT, *self.gamma_params[month])
            SPI = stats.norm.ppf(cdf, loc=0, scale=1)
        else:
            SPI=np.nan
        return SPI


    def make_conv_dataset(self):
        self.sorted_PRCPTOT = np.convolve(self.target_PRCPTOT, np.ones(3), mode='same')[1:-1]
        self.sorted_date_arr = self.in_date_arr[2:]
        return self
