#!/usr/bin/eng python3
# -*- coding: utf-8 -*-
# 大気外全天日射量(W/m^2)を計算する

# %%
import numpy as np
import pandas as pd
if __name__=='__main__':
    from calc_sinh import calc_sinh
else:
    from .calc_sinh import calc_sinh
def DaylightOutsideTheAtmosphere(date:pd.Timestamp, lat:float, lon:float, Ls:int=135, mode='radiation'):
    """指定地点・時刻の大気外全天日射量(W/m^2)を求める

    Args:
        date (pd.Timestamp): 指定時刻 (デフォルトではUTC)\n
        lat (float): 指定地点の緯度\n
        lon (float): 指定地点の軽度\n
        Ls (int): 標準子午線の経度\n
        mode (str): 'radiation:だと大気外全天日射量[W m-2], 'ppfd'だとPPFD[μmol m-2 s-1]

    Returns:
        Q: 大気外全天日射量 (W/m^2)
        Q: 大気上端PPFD (μ mol m^-2 s^-1)
    """
    sinh = calc_sinh(
        lat=lat, lon=lon,
        date=date,
        Ls=Ls
    )

    np.rad2deg(np.arcsin(sinh))
    Gamma=2 * np.pi * ((date.dayofyear-1)/365)
    if (type(Gamma)!=np.ndarray)&(type(Gamma)!=float):
        Gamma=Gamma.values
    if (type(sinh)!=np.ndarray)&(type(Gamma)!=float):
        sinh =sinh.values


    E0 = (1.000110 + 0.034221*np.cos(Gamma)+0.001280*np.sin(Gamma)+0.000719*np.cos(2*Gamma)+0.000077*np.sin(2*Gamma))
    if      mode=='radiation':
        Q = 1367 * E0 * sinh
    elif    mode=='ppfd':
        Q = 2405.13 * E0 * sinh
    return Q

if __name__=='__main__':

    date = pd.to_datetime('1991/1/1')
    daily_date_arr = pd.date_range(
        f'{date.strftime("%Y/%m/%d")}-0:00', f'{date.strftime("%Y/%m/%d")}-23:59:59', freq='S')

    da = DaylightOutsideTheAtmosphere(
        date=daily_date_arr,
        lat=40, lon=140, Ls=135
    )
    print(da)

# %%