#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mR95pMonthly2D: 月次mR95pの2Dを計算する.
# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime

if __name__=='__main__':
    from mR95p import mR95pMonthlyBase
else:
    from .mR95p import mR95pMonthlyBase

import warnings
warnings.simplefilter('ignore')

# %%
if __name__=='__main__':
    date_arr = pd.to_datetime(np.arange(
        datetime.datetime(1991,1,1),
        datetime.datetime(2020,12,31,1),
        datetime.timedelta(days=1)
    ))

    all_img = np.zeros((200,200,len(date_arr)))

    for i, date in enumerate(date_arr):
        get_img = np.fromfile(
            f'D:/ResearchData3/Level3/chirps005_RAW_f32/chirps_005.A{date.year}{str(date.dayofyear).zfill(3)}.float32_h1600w1500.raw',
            count=1600*1500, dtype=np.float32
        ).reshape(1600, 1500)
        all_img[:,:,i] = get_img[800:1000, 800:1000]
        if date.dayofyear==1:
            print(date.year)


# %%
class mR95pMonthly2D(mR95pMonthlyBase):
    def __init__(self, normal_start_year=1991, normal_end_year=2020):
        """月次mR95pを計算する(2D)

        Args:
            normal_start_year (int): 平年値算出に使うデータの開始年
            normal_end_year (int): 平年値算出に使うデータの終了年
        """
        super().__init__(normal_start_year, normal_end_year)
    
    def calc_mRRwn95(self, rain30_arr, window_half=7, min_sample_size=30, Rnnmm=10):
        """各平年値(mRRwn95, PPT)を計算する

        Args:
            rain30_arr (Array like (3D)): 30年平年値を算出するために使用するデータ
            window_half (int, optional): ウィンドウサイズ. Defaults to 7.
            min_sample_size (int, optional): 計算に最低限必要な降雨日数(30年間). Defaults to 30.
            Rnnmm (float): ユーザー定義の最低豪雨しきい値. Defaults to 10.

        """
        h,w,_ = rain30_arr.shape
        
        self.mRRwn95 = np.zeros((h, w, 366))
        for i, doy in enumerate(range(1, 365)):
            using_doy_arr = np.arange(doy-window_half, doy+window_half+1)
            using_doy_arr = np.where(using_doy_arr<=0, using_doy_arr+365, using_doy_arr)  # 使用するDOYリストをまとめる


            using_rain30_arr = rain30_arr[:,:,np.isin(self.normal_date_arr.dayofyear, using_doy_arr)]  # 使用するrain30リストをまとめる
            rainy_ppt_arr = np.where(using_rain30_arr>0, using_rain30_arr, np.nan)  # 雨の日の降水量以外をnullに変換
            rainy_days_arr = np.nansum(~np.isnan(rainy_ppt_arr), axis=2)  # 雨の日の日数をカウント

            # mRRwn95を計算
            self.mRRwn95[:,:,i] = np.where(
                rainy_days_arr<min_sample_size,
                Rnnmm,
                np.nanpercentile(rainy_ppt_arr, 95, axis=2)
            )
            if doy%10==0:
                print(f'calc mRRwn95 (doy:{str(doy).zfill(3)})')  # CHECK LOG
            del using_doy_arr, using_rain30_arr, rainy_ppt_arr, rainy_days_arr  # メモリの開放
        self.mRRwn95[:,:,365-1] = self.mRRwn95[:,:,366-1]
        return self
    
    def calc_PPT_mean(self, rain30_arr):
        """各スパンごとの平均総降水量を計算(オーバーライド)

        Args:
            rain30_arr (Array like, 1D): 30年平年値を算出するために使用するデータ
        """
        h,w,_ = rain30_arr.shape
        self.PPT_mean = np.zeros((h,w,12*30))

        for i,month in enumerate(range(1, 12+1)):
            using_ppt_arr = rain30_arr[:,:,self.normal_date_arr.month==month]
            self.PPT_mean[:,:,i] = np.nansum(using_ppt_arr, axis=2)/30
        return self
    
    def calc_mR95pT(self, rain_arr, start_year, end_year):
        """入力データ・入力期間の期間毎mR95p, mR95pTを計算する

        Args:
            rain_arr (Array like): 計算したい期間の降水量データ
            start_year (int): 計算したい期間の開始年
            end_year (int): 計算したい期間の終了年
        """

        h,w,_ = rain_arr.shape
        target_date_arr = pd.to_datetime(np.arange(
            datetime.datetime(start_year, 1, 1),
            datetime.datetime(end_year, 12, 31, 1),
            datetime.timedelta(days=1)
        )
        )
        self.mR95p = np.zeros((h,w,(end_year-start_year+1)*12))
        self.mR95pT = np.zeros_like(self.mR95p)

        # 95%ile値を超えたPPTのみ残し,超えなかった分をnanにする(メモリは節約).
        rain_arr = np.where(
            rain_arr>=self.mRRwn95[:,:, target_date_arr.dayofyear-1],
            rain_arr,
            np.nan
        )

        cnt=0
        for year in range(start_year, end_year+1):
            for month in range(1, 12+1):
                using_ppt_arr = rain_arr[:,:,(target_date_arr.year==year)&(target_date_arr.month==month)]
                mR95p_img = np.nansum(using_ppt_arr, axis=2)
                mR95pT_img = np.where(
                    self.PPT_mean[:,:,month-1]==0,
                    np.nan,
                    mR95p_img/self.PPT_mean[:,:,month-1]
                )
                self.mR95p[:,:,cnt] = mR95p_img
                self.mR95pT[:,:,cnt] = mR95pT_img
                cnt+=1
            print(f'calc mR95pT ({year}/{str(month).zfill(2)})')

        return self
    
# %%
if __name__=='__main__':
    m95m2d = mR95pMonthly2D()
    m95m2d.calc_normalyear(all_img)
    m95m2d.calc_mR95pT(all_img, 1991, 2020)