#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TimeVarying_CofficientModel.py: 時変係数モデル

# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.api as sm

# %%
class TimeVarying_CofficientModel(sm.tsa.statespace.MLEModel):
    param_names = []
    start_params = []
    def __init__(self, endog, exog):
        """時変係数 状態空間モデル

        y_t     = x_t + H_t
        x_{t+1} = T*x_t + c_t + Q_t
        c_t     = state_intercept @ exog.T
        Ht: 観測誤差
        Qt: 状態誤差
        

        Args:
            endog (_type_): _description_
            exog (_type_): _description_
        """


        exog = np.asarray(exog)
        super().__init__(endog, exog=exog, k_states=1, initialization='diffuse')
        if exog.ndim==1:
            self.k_exog = 1
        elif exog.ndim==2:
            self.k_exog = exog.shape[1]
        
        # パラメータの初期設定

        self.param_names = ['T']+[f'B{i}' for i in range(self.k_exog)]+['Ht', 'Qt'] #推定するパラメータを指定
        self.start_params = [1]+[1]*self.k_exog+[.1,.1] #推定するパラメータの初期値

        # ばらつきのパラメータの開始位置
        self.std_start = 1+self.k_exog
        # Z = I,上記式のZtに当たる部分は今回単位行列になる
        self['design', 0, 0] = 1.
        # R = I,上記式のRtに当たる部分は今回単位行列になる
        self['selection', 0, 0] = 1.

        # c_tを時変に設定します
        # c_t = A * exp(B/z)  zは外生変数
        self['state_intercept'] = np.zeros((1, self.nobs))

    def clone(self, endog, exog, **kwargs):
        return self._clone_from_init_kwds(endog, exog=exog, **kwargs)

    def transform_params(self, params):
        # 分散は正数である必要があるので一旦2乗する
        params[self.std_start:] = params[self.std_start:]**2
        return params

    def untransform_params(self, params):
        # 2乗したものを1/2乗して元の大きさに戻す（平方根）
        params[self.std_start:] = params[self.std_start:]**0.5
        return params

    def update(self, params, **kwargs):
        # 更新するための指定です
        params = super().update(params, **kwargs)
        # T = T
        self['transition', 0, 0] = params[0]
        # c_t = A * z_t
        self['state_intercept', 0, :] = np.dot(params[1:self.std_start], self.exog.T)
        # Ht
        self['obs_cov', 0, 0] = params[self.std_start]
        # Qt
        self['state_cov', 0, 0] = params[self.std_start+1]