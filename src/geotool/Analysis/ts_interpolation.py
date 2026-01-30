#!/usr/bin/env python-3
# -*- coding:utf-8 -*-
# 測量標高値を線形補完し、SAR観測日の推定標高値を算出する
import numpy as np

def ts_interpolation(sokuryo_Zs, sokuryo_dates_all, sar_date):
    """測量標高値を線形補完し、SAR観測日の推定標高値を算出する。

    Args:
        sokuryo_Zs (pd.TimeSeriesIndex): 測量標高値の時系列データ
        sokuryo_dates_all (pd.TimeSeriesIndex): 測量日（実際には観測していない日も含むすべて）
        sar_date (pd.TimeSeriesIndex): SAR観測日
    Return:
        SAR観測日における測量値(単位は入力値準拠)
    """
    
    sokuryo_dates_used = sokuryo_dates_all[~np.isnan(sokuryo_Zs)]  # 実際に対象地点で測量した日付
    dates_diff_SOKURYOvSAR = (sokuryo_dates_used - sar_date).days  # 各測量日とSAR観測日との日数
    pre_sokuryo_date  = sokuryo_dates_used[dates_diff_SOKURYOvSAR==np.nanmax(dates_diff_SOKURYOvSAR[dates_diff_SOKURYOvSAR<0])][0]  # SAR観測日の直前の測量日
    post_sokuryo_date = sokuryo_dates_used[dates_diff_SOKURYOvSAR==np.nanmin(dates_diff_SOKURYOvSAR[dates_diff_SOKURYOvSAR>=0])][0]  # SAR観測日の直後の測量日

    pre_sokuryo_Z  = sokuryo_Zs[sokuryo_dates_all==pre_sokuryo_date][0]  # SAR観測日直前の測量標高値
    post_sokuryo_Z = sokuryo_Zs[sokuryo_dates_all==post_sokuryo_date][0]  # SAR観測日直後の標高測量値

    sar_sokuryo_Z = pre_sokuryo_Z + (post_sokuryo_Z - pre_sokuryo_Z) / (post_sokuryo_date-pre_sokuryo_date).days * (sar_date-pre_sokuryo_date).days

    return sar_sokuryo_Z