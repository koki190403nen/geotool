#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDVI異常を検出するためのクラス

前処理(smoothing)、季節調整、異常検知の順に行う
"""

# %%
import numpy as np
from scipy import stats
from statsmodels.tsa.seasonal import STL
from ..Smoothing import whittaker_smooth

# %%
class ExtractNDVIAnomaly:
    """
    NDVI異常を検知する

    Attributes
    ---------
    input_ndvi_arr: numpy.array
        解析対象のndvi配列

    period : int
        データのサンプリング周期

    anomaly_dict : dict
        各メソッドにより計算された異常値が記録される

    smoothing_method: function
        平滑化手法

    seasonal_adjustment_method : function
        季節調整法

    """

    def __init__(self, ndvi_arr=None, period=23):
        """
        Parameters
        ----------
        ndvi_arr : numpy.array, default None
            解析対象のndvi配列
        """
        self.ndvi_arr = ndvi_arr  # 入力ndvi array
        self.period = period  # サンプリング周期
        self.anomaly_dict = {}  # 異常値の記録
        self.smoothing_method = whittaker_smooth  # スムージング法
        self.seasonal_adjustment_method = STL  # 季節調整法
    
    def fit(self, ndvi_arr=None, smoothing_kwargs=None):
        """
        平滑化, 季節調整, 異常検知の順にメソッドを適用する

        Parameters
        ----------
        ndvi_arr : numpy.array, default None
            解析対象のndvi 配列
        smoothing_kwargs : dict, default None
            平滑化のパラメータ(辞書型)

        Returns
        -------
        anomaly_dict : dict
            異常値の出力結果を辞書型で返す(時間分解能が1年のもの)
        """

        # 新たな入力値を受け取った際の処理
        if ndvi_arr is not None:
            self.ndvi_arr = ndvi_arr

        smoothed_arr = self.smoothing_method(self.ndvi_arr, **smoothing_kwargs)  # 平滑化の実行
        seasonalized_res = self.seasonal_adjustment_method(smoothed_arr, period=self.period).fit()  # 季節調整の実行

        # ここからanomalyの計算
        self.extract_lulc_change(smoothed_arr - seasonalized_res.trend, p=0.05)  # lulcの変化を検出
    
    def extract_lulc_change(self, ndvi_arr,  p=0.05):
        """
        土地被覆の変化を検知する

        Parameters
        ----------
        ndvi_arr : numpy.array
            解析対象のndvi配列
        p : float, default 0.05
            統計検定に利用するp値, デフォルトは0.05

        Returns
        -------
        lulc_sim_ls : list
            前年と比較したseasonal成分の近似度を出力する
            近似度の測定にはスピアマンの相関係数を利用
        
        Notes
        -----
        lulc_sim_lsはself.anomaly_dictにkey='lulc_sim'として記録
        """

        seasonal_each_arr = ndvi_arr.reshape(-1, self.period)  # (年, sampling日)の2d arrayに変換

        lulc_sim_ls = [1]  # 最初の年度は計算できないので1(完全一致)とする
        for yi in range(seasonal_each_arr.shape[0] - 1):
            before_seasonal = seasonal_each_arr[yi]  # 前年のseasonal成分
            after_seasonal = seasonal_each_arr[yi+1]  # 後年のseasonal成分
            res_r, res_p = stats.spearmanr(before_seasonal, after_seasonal)

            if res_p < p:
                lulc_sim_ls.append(res_r)
            else:
                lulc_sim_ls.append(np.nan)  # 帰無仮説を棄却できない場合はnull埋め

        
        self.anomaly_dict['lulc_sim'] = lulc_sim_ls  
        return lulc_sim_ls


    def test(self):
        """
        テスト用関数
        """
        print('test')


    

    