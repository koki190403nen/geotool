# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import json
import datetime

if __name__=='__main__':
    from mR95p import mR95pBase
else:
    from .mR95p import mR95pBase

def make_r95pT_df_from_amedas(csv_path):
    df = pd.read_csv(csv_path, index_col=0)


    daily_date_arr = pd.to_datetime(df.index)
    target_date_arr = pd.to_datetime(
        [f'{year}/{doy}' for year in range(1991, 2020+1) for doy in range(1, 366, 16)] + ["2021/1"],
        format='%Y/%j')


    ppt_arr = df['PPT'].values

    mr95p   = mR95pBase()
    mRRwn95 = mr95p.calc_mRRwn95(ppt_arr).mRRwn95
    RRwn95  = np.percentile(ppt_arr[ppt_arr!=0], 95)
    mRRwn95_doy = np.array([i for i in range(1, 366+1)])


    mR95p_ls    = []
    R95p_ls     = []
    PRCPTOT_ls  = []
    daycnt_ls   = []

    for i, target_date in enumerate(target_date_arr):
        if target_date.year==2021:
            break
        using_date_arr  = pd.date_range(target_date, target_date_arr[i+1]-datetime.timedelta(days=1), freq='D')
        using_pixel_arr = np.isin(daily_date_arr, using_date_arr)
        using_ppt_arr   = ppt_arr[using_pixel_arr]


        daycnt_ls.append(len(using_date_arr))
        PRCPTOT_ls.append(np.nansum(using_ppt_arr))
        mR95p_ls.append(np.nansum(using_ppt_arr[using_ppt_arr>=mRRwn95 [np.isin(mRRwn95_doy, using_date_arr.dayofyear)]]))
        R95p_ls.append(np.nansum(using_ppt_arr[using_ppt_arr>=RRwn95]))

    daycnt_arr  = np.array(daycnt_ls)
    PRCPTOT_arr = np.array(PRCPTOT_ls)
    mR95p_arr   = np.array(mR95p_ls)
    R95p_arr    = np.array(R95p_ls)

    mean_PRCPTOT = np.nanmean((PRCPTOT_arr / daycnt_arr * 16).reshape(-1, 23), axis=0)

    mR95pT_arr = np.where(mean_PRCPTOT!=0,
                          ((mR95p_arr/daycnt_arr * 16).reshape(-1, 23) / mean_PRCPTOT),
                          0).flatten()
    R95pT_arr  = np.where(PRCPTOT_arr!=0,
                          R95p_arr / PRCPTOT_arr,
                          0)


    out_df = pd.DataFrame({
        'PRCPTOT'   : PRCPTOT_arr,
        'R95p'      : R95p_arr,
        'mR95p'     : mR95p_arr,
        'R95pT'     : R95pT_arr,
        'mR95pT'    : mR95pT_arr
    }, index=target_date_arr[:-1])
    dataset = {
    'mRRwn95': list(mRRwn95),
    'RRwn95' : RRwn95
    }
    return out_df, dataset

# %%
if __name__=='__main__':
    make_r95pT_df_from_amedas('../../sample/Amedas/Nigata.csv')[0].to_csv('../../sample/dataset/Nigata.csv')