 #!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 一日あたり大気上端PARを計算する
# %%
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
if __name__=='__main__':
    from DaylightOutsideTheAtmosphere import DaylightOutsideTheAtmosphere
else:
    from .DaylightOutsideTheAtmosphere import DaylightOutsideTheAtmosphere

lat = np.array([40, 40])
lon = np.array([139, 139])
def calc_dailypar(date:pd.Timestamp, lat:float, lon:float, accuracy='60S'):
    """日平均PAR [Ein/m^2/s/day]を求める

    Args:
        date (pd.Timestamp): 指定日
        lat (float): 指定緯度 (2D 可能)
        lon (float): 指定軽度 (2D 可能)
        accuracy (str, optional): 計算精度. Defaults to '60S'.

    Returns:
        _type_: _description_
    """

    daily_date_arr = pd.date_range(
        f'{date.strftime("%Y/%m/%d")}-0:00', f'{date.strftime("%Y/%m/%d")}-23:59:59', freq=accuracy)

    Daylight = DaylightOutsideTheAtmosphere(date=daily_date_arr, lat=lat, lon=lon, Ls=0)
    if len(Daylight.shape)==3:
        dailypar = np.nanmean(np.where(Daylight>0, Daylight*0.4641 * (0.1193/0.3), np.nan), axis=2)
    elif len(Daylight.shape)==1:
        dailypar = np.nanmean(np.where(Daylight>0, Daylight*0.4641 * (0.1193/0.3), np.nan))
    return dailypar

# %%
if __name__=='__main__':
    h,w = 1600, 1500
    
    date = pd.to_datetime('1991/1/1')
    lon_img = np.zeros()
    lat = np.array([[35, 40]])

    calc_dailypar(
        date=date,
        lat=lat,lon=lon,
        #lat=35, lon=140,
        #Ls=135
    )


# %%
