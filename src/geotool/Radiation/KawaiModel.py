#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

def rmse(y_obs, y_pred):
    """RMSE計算用関数

    Args:
        y_obs (_type_): _description_
        y_pred (_type_): _description_

    Returns:
        物理量, %
    """
    RMSE =  np.sqrt(np.nanmean((y_obs-y_pred)**2))
    
    return RMSE, RMSE / np.nanmean(y_obs)

class KawaiModel:
    def __init__(self, X_train, y_train, B03_train, B03_threshold=0.2):
        """ひまわり観測データから日射量を推定するモデル (天気分解)

        Args:
            X_train (pd.DataFrame): 説明変数 (必要なバンドのみあらかじめ選択しておく)
            y_train (Array like): 応答変数 (地上観測 全天 or 散乱 日射量)
            B03_train (Array Like): B03の値
            B03_threshold (float): 天気を分類するために使用するB03のしきい値. Defaults to 0.2.
        """
        self.X_train        = X_train
        self.y_train        = y_train
        self.B03_train      = B03_train
        self.B03_threshold  = B03_threshold
        
        self.models = []
    
    def fit(self, engine='statsmodels'):
        """モデルの学習

        Args:
            engine (str, ): 学習モデルで使用するライブラリ. Defaults to 'statsmodels' or 'sklearn'.
        """
        # B03_threshold以下のモデルの学習
        
        if engine=='statsmodels':
            lr1 = sm.OLS(self.y_train[self.B03_train <  self.B03_threshold], self.X_train[self.B03_train <  self.B03_threshold]).fit()
            lr2 = sm.OLS(self.y_train[self.B03_train >= self.B03_threshold], self.X_train[self.B03_train >= self.B03_threshold]).fit()
        
        elif engine=='sklearn':
            lr1 = LinearRegression().fit(self.X_train[self.B03_train <  self.B03_threshold], self.y_train[self.B03_train <  self.B03_threshold])
            lr2 = LinearRegression().fit(self.X_train[self.B03_train >= self.B03_threshold], self.y_train[self.B03_train >= self.B03_threshold])
        

        self.models = [lr1, lr2]
        return self
    
    def predict(self, X_test, B03_test):
        """学習済みモデルを使用して予測する

        Args:
            X_test (pd.DataFrame): 説明変数
            B03_test (Array like): B03の値

        Returns:
            _type_: _description_
        """

        y_pred = np.where(
            B03_test < self.B03_threshold,
            self.models[0].predict(X_test),
            self.models[1].predict(X_test)
        )
        
        return y_pred

    
    

class Kawai_Seasonal:
    def __init__(self, X_train, y_train, B03_train, date_train, B03_threshold=0.2):
        """ひまわり観測データから日射量を推定するモデル (天気分解×季節分解)

        Args:
            X_train (pd.DataFrame): 説明変数 (必要なバンドのみあらかじめ選択しておく)
            y_train (Array like): 応答変数 (地上観測 全天 or 散乱 日射量)
            B03_train (Array Like): B03の値
            date_train (pd.datetimeIndex): 学習データの日付ラベル
            B03_threshold (float): 天気を分類するために使用するB03のしきい値. Defaults to 0.2.
        """
        self.X_train    = X_train
        self.y_train    = y_train
        self.B03_train  = B03_train
        self.date_train = date_train
        self.B03_threshold = B03_threshold
        
        self.sea_bool_train = {
            'spring': np.isin(self.date_train.month, [2,3,4,5,6]),
            'summer': np.isin(self.date_train.month, [5,6,7,8,9]),
            'autumn': np.isin(self.date_train.month, [8,9,10,11,12]),
            'winter': np.isin(self.date_train.month, [11, 12, 1,2,3])
        }
        

    def fit(self, engine='statsmodels'):
        """モデルの学習

        Args:
            engine (str, ): 学習モデルで使用するライブラリ. Defaults to 'statsmodels' or 'sklearn'.
        """

        self.models = {}
        for key, vals in self.sea_bool_train.items():
            kmodel = KawaiModel(self.X_train[vals], self.y_train[vals], self.B03_train, self.B03_threshold)
            kmodel.fit(engine=engine)
            self.models[key] = kmodel
        
    def predict(self, X_test, B03_test, date_test):
        """学習済みモデルを使用して予測する

        Args:
            X_test (pd.DataFrame): 説明変数
            B03_test (Array like): B03の値
            date_test (pd.DatetimeIndex): 説明変数の日付ラベル

        """
        
        y_pred = \
            np.where(
                np.isin(date_test.month,[3,4,5]),
                self.models['spring'].predict(X_test, B03_test),
            np.where(
                np.isin(date_test.month,[6,7,8]),
                self.models['summer'].predict(X_test, B03_test),
            np.where(
                np.isin(date_test.month,[9,10,11]),
                self.models['autumn'].predict(X_test, B03_test),
            np.where(
                np.isin(date_test.month,[12, 1, 2]),
                self.models['winter'].predict(X_test, B03_test), np.nan
            ))))
        
        return y_pred
    
