#/usr/bin/env python3
# -*- coding: utf-8 -*-
# 直達光と散乱光を分離する
# %%
import numpy as np
if __name__=='__main__':
    from calc_sinh import calc_sinh
else:
    from .calc_sinh import calc_sinh

# %%
# 晴天指数を求める
def clear_sky_index(lat, lon, date, Ls, I):
    sinh = calc_sinh(lat, lon, date, Ls)  # sinhの計算
    I_SC = 1367  # 太陽定数(W/m2)
    R_0 = 1  # 太陽と地球の距離の平均
    R = 1  # ある時刻dateにおける太陽と地球の距離の平均
    I0 = I_SC * (R_0 / R)**2 * sinh  # 大気外水平面日射量(W/m2)
    kt = I / I0  # 晴天指数
    return kt

# 直達散乱分離モデル(川井10minモデル)
def kawai_1hour(lat, lon, date, Ls, I):
    """全天日射量から水平面散乱日射量を求める

    Args:
        lat (float): 観測地点の緯度
        lon (float): 観測地点の経度
        date (datetime.datetime): 観測時刻
        Ls (float): 標準子午線の経度(明石の135°)
        I (float): 観測された全天日射量(W/m2)

    Returns:
        Id (float): 分離された散乱日射量(W/m2)
    """

    kt = clear_sky_index(lat, lon, date, Ls, I)

    if kt < 0.250:
        kd = 1.000
    elif (0.250<=kt)&(kt<=0.795):
        kd = 0.782 + 3.112 * kt - 10.894 * kt**2 + 7.511 * kt**3
    elif kt > 0.795:
        kd = 0.145

    Id = kd * I
    return Id

