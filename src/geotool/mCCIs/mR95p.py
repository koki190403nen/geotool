#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mR95pを計算するクラス

# %%
from operator import index
import numpy as np
import datetime
import pandas as pd
from matplotlib import pyplot as plt

# %%
# 各DOYごとにR95inを算出する

class mR95pBase:
    def __init__(self, normal_start_year=1991, normal_end_year=2020):
        """mR95pを計算する

        Args:
            normal_start_year (int): 平年値算出に使うデータの開始年
            normal_end_year (int): 平年値算出に使うデータの終了年
        """
        self.normal_start_year = normal_start_year  # 平年値の計算開始年
        self.normal_end_year = normal_end_year  # 平年値の計算終了年
        
        # 平年値のdateリスト
        self.normal_date_arr = pd.to_datetime(np.arange(
            datetime.datetime(normal_start_year, 1, 1),
            datetime.datetime(normal_end_year, 12, 31, 1),
            datetime.timedelta(days=1)
            ))
        self.mRRwn95 = None  # mRRwn95
        self.PPT_mean = None  # 平年値の計算
        self.mR95p = None  # 月別のmR95p(mm)
        self.mR95pT = None  # 月別のmR95pを30年平均降水量で正規化

    def calc_mRRwn95(self, rain30_arr, window_half=7, min_sample_size=30, Rnnmm=10):
        """各平年値(mRRwn95, PPT)を計算する

        Args:
            rain30_arr (_type_): 30年平年値を算出するために使用するデータ
            window_half (int, optional): ウィンドウサイズ. Defaults to 7.
            min_sample_size (int, optional): 計算に最低限必要な降雨日数(30年間). Defaults to 30.
            Rnnmm (float): ユーザー定義の最低豪雨しきい値. Defaults to 10.

        """

        doy_arr = self.normal_date_arr.dayofyear.values  # 入力データのDOYリスト
        
        no366_ppt_arr = rain30_arr[doy_arr!=366].reshape(-1, 365)  # DOY366は計算しない
        clean_ppt_arr = np.concatenate([
            no366_ppt_arr.reshape(-1, 365)[:, -1*window_half:],
            no366_ppt_arr.reshape(-1, 365),
            no366_ppt_arr.reshape(-1, 365)[:, :window_half]
        ], axis=1)
        
        RRwn95_ls = []
        for i in range(365):
            target_period = clean_ppt_arr[:, i:i+window_half*2+1]
            if len(target_period[target_period!=0])<min_sample_size:
                RRwn95 = Rnnmm
            else:
                RRwn95 = np.percentile(target_period[target_period!=0], 95)
            RRwn95_ls.append(RRwn95)
        RRwn95_ls.append(RRwn95)  # DOY366用のデータを入れる
        self.mRRwn95 = np.array(RRwn95_ls)
        self.mRRwn95[self.mRRwn95<Rnnmm] = Rnnmm

        return self
    
    def calc_PPT_mean(self, rain30_arr):
        pass

    def calc_normalyear(self, rain30_arr, window_half=7, min_sample_size=30, Rnnmm=10):
        """各平年値(mRRwn95と期間別平均総降水量)を計算する

        Args:
            rain30_arr (Array like): 平年値計算に使用する降水量データ(30年分)
            window_half (int): 各DOY計算に使用するウィンドウのサイズ. Defaults to 7.
            min_sample_size (int): 最低限必要な降雨日の日数. Defaults to 30.
            Rnnmm (float): ユーザー定義の最低豪雨しきい値. Defaults to 10.

        """
        self.calc_mRRwn95(rain30_arr, window_half, min_sample_size, Rnnmm)
        self.calc_PPT_mean(rain30_arr)
        return self

    def set_normalyear(self, RRwn95, ppt_mean):
        """平年値がすでに計算済みの時, クラスにセットする

        Args:
            RRwn95 (Array like (n+1D, 366)): DOY別95%ileしきい値
            ppt_mean (Array like, (n+1D, ex.12)): 期間別平均総降水量
        """
        self.mRRwn95 = RRwn95
        self.PPT_mean = ppt_mean
        return self
    
    def calc_mR95pT_single(self, rain_arr, start_doy, end_doy):
        """mR95pTを一つだけ推定する

        Args:
            rain_arr (Array like): 入力データ
            start_doy (int): 入力データの開始DOY
            end_doy (int): 入力データの終了DOY

        Returns:
            Array like: 入力降水量データから求められたmR95pT
        """
        threshold_arr = self.mRRwn95[start_doy-1:end_doy-1]
        mR95p = np.nanmean(rain_arr[rain_arr>=threshold_arr])
        PPT_mean = np.nanmean(self.PPT_mean[start_doy-1:end_doy-1])
        return mR95p / PPT_mean

class mR95pMonthlyBase(mR95pBase):
    def __init__(self, normal_start_year, normal_end_year):
        super().__init__(normal_start_year, normal_end_year)

    def calc_PPT_mean(self, rain30_arr):
        pass

    def calc_mR95pT(self, rain_arr, start):
        pass
