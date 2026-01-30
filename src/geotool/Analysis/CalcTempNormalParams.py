#!/usr/bin/env python3
# -*- coding : uft-8 -*-
# CalcTempNormalParams.py: 気温の平年値パラメータを計算する
#%%
import numpy as np
import pandas as pd

def calc_temp_normal_params(
    temp1day_df,
    temp_element='MeanTEMP',
    input_min_year=1991):
    # 処理

    mu_ls =[]
    sigma_ls=[]
    doy_ls=[]

    # doyごとに平年値を算出
    for doy in np.arange(1, 365+1):

        get_doy_ls = []
        # 周辺5日間のデータを使用してデータ量を増やす(5CDの実行)
        for delta in np.arange(-2, 2+1):
            get_doy = doy + delta
            if get_doy<=0:  # 前年にわたる時
                get_doy = get_doy+ 365
                min_year = input_min_year-1

            elif get_doy>=366:
                get_doy = get_doy - 365
                min_year = input_min_year+1

            else:
                min_year = input_min_year
            get_doy_ls.append(get_doy)
            year_ls = list(np.arange(min_year, min_year+30))
        # /*5CDここまで*/

        # ブートストラップ実行前のtempデータのリスト(length:150)
        before_bootstrap_value = temp1day_df.query(
            f'year=={year_ls} and doy=={get_doy_ls}'
        )[temp_element].values

        # ブートストラップ実行後のtempデータのリスト(length: 4205)
        all_value = np.random.choice(before_bootstrap_value, 29*5*29)

        # 各統計量の算出
        mu = np.nanmean(all_value)
        sigma = np.nanstd(all_value, ddof=1)

        mu_ls.append(mu)
        sigma_ls.append(sigma)
        doy_ls.append(doy)
    return np.array(mu_ls), np.array(sigma_ls), np.array(doy_ls)
# %%
