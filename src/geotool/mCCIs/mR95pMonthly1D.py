#!/usr/bin/env pythno3
# -*- coding: utf-8 -*-
# mR95pMonthly2D: 月別mR95pの1Dデータ(時間方向のみ)を計算
# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime

if __name__=='__main__':
    from mR95p import mR95pMonthlyBase
else:
    from .mR95p import mR95pMonthlyBase


class mR95pMonthly1D(mR95pMonthlyBase):
    def __init__(self, normal_start_year, normal_end_year):
        """mR95pを計算する(時間解像度は1ヶ月)

        Args:
            normal_start_year (int): 平年値算出に使うデータの開始年
            normal_end_year (int): 平年値算出に使うデータの終了年
        """
        super().__init__(normal_start_year, normal_end_year)

    def calc_PPT_mean(self, rain30_arr):
        """各スパンごとの平均総降水量を計算(オーバーライド)

        Args:
            rain30_arr (Array like, 1D): 30年平年値を算出するために使用するデータ
        """
        year_arr = self.normal_date_arr.year.values
        month_arr = self.normal_date_arr.month.values
        PRCP_ls = []
        for year in range(self.normal_start_year, self.normal_end_year+1):
            for month in range(1, 12+1):
                all_rain_arr = np.where(
                    (year_arr==year)&(month_arr==month),
                    rain30_arr, np.nan
                )
                PRCP = np.nansum(all_rain_arr)
                PRCP_ls.append(PRCP)
        self.PPT_mean = np.nanmean(np.array(PRCP_ls).reshape(-1, 12), axis=0)
        return self

    def calc_mR95pT(self, rain_arr, start_year, end_year):
        """入力データ・入力期間の期間毎mR95p, mR95pTを計算する

        Args:
            rain_arr (Array like): 計算したい期間の降水量データ
            start_year (int): 計算したい期間の開始年
            end_year (int): 計算したい期間の終了年

        """

        date_arr = pd.to_datetime(np.arange(
            datetime.datetime(start_year, 1, 1),
            datetime.datetime(end_year, 12, 31, 1),
            datetime.timedelta(days=1)
            ))
        doy_arr = date_arr.dayofyear.values
        year_arr = date_arr.year.values
        month_arr = date_arr.month.values
        
        year_unique = np.unique(year_arr)[~np.isnan(np.unique(year_arr))]
        start_year = int(year_unique[0])
        end_year = int(year_unique[-1])
        R95p_ls = []
        threshold_arr = self.mRRwn95[list((doy_arr-1).astype(int))]
        for year in range(start_year, end_year+1):
            for month in range(1, 12+1):
                over_rain_arr = np.where(
                    (year_arr==year)&(month_arr==month)&(rain_arr>=threshold_arr),
                    rain_arr, np.nan
                )
                R95p = np.nansum(over_rain_arr)
                R95p_ls.append(R95p)
        self.mR95p = np.array(R95p_ls)
        self.mR95pT =(self.mR95p.reshape(-1, 12)/self.PPT_mean).flatten()  # mR95p/PPT_meanを計算
        self.mR95pT = np.where(~np.isnan(self.mR95pT), self.mR95pT, 0)
        return self

# %%
if __name__=='__main__':
    df = pd.read_csv('../../sample/prcp_sample.csv', index_col=0)
    area='Zanbia1'
    print(df.head())
    normal_ppt = df.query('year>=1991 & year<=2020')[area].values
    target_ppt = df.query('year>=1991 & year<=2020')[area].values
    mr95mon = mR95pMonthly1D(1991, 2020)
    res = mr95mon.calc_normalyear(normal_ppt, Rnnmm=10).calc_mR95pT(target_ppt, 1991, 2020)
    
    plt.bar(range(366), res.mRRwn95)
    plt.show()