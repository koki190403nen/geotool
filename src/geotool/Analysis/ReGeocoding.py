#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ReGeocoding.py: 逆ジオコーディングを実行（地理院API）
# %%
import requests
import pandas as pd
from pathlib import Path
def ReGeocoding(lat, lon):
    """逆ジオコーディングする関数

    Args:
        lat (float): 緯度
        lon (float): 経度

    Returns:
        [muniCd, pref, city, lv01Nm] : [muniコード, 都道府県名, 市町村名, 市町村より下の住所]
    """
    muni_df = pd.read_csv(Path(__file__).resolve().parent.joinpath(f'./municode.csv'))
    res = requests.get(f'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress?lat={lat}&lon={lon}')
    muniCd = int(res.json()['results']['muniCd'])

    pref = muni_df.query(f'muniCd=={muniCd}')['chiriin_pref_name'].values[0]
    city = muni_df.query(f'muniCd=={muniCd}')['chiriin_city_name'].values[0]
    lv01Nm = res.json()['results']['lv01Nm']

    return muniCd, pref, city,lv01Nm