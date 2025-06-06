#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ReGeocoding.py: 逆ジオコーディングを実行（地理院API）
# %%
import requests
import pandas as pd
import os
from pathlib import Path
def ReGeocoding(lat, lon, usr, passwd):
    os.environ['http_proxy'] = f'http://{usr}:{passwd}@prtyo1.n-koei.co.jp:8080'
    os.environ['https_proxy'] = f'http://{usr}:{passwd}@prtyo1.n-koei.co.jp:8080'

    muni_df = pd.read_csv(Path(__file__).resolve().parent.joinpath(f'./municode.csv'))
    res = requests.get(f'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress?lat={lat}&lon={lon}')
    muniCd = int(res.json()['results']['muniCd'])

    pref = muni_df.query(f'muniCd=={muniCd}')['chiriin_pref_name'].values[0]
    city = muni_df.query(f'muniCd=={muniCd}')['chiriin_city_name'].values[0]
    lv01Nm = res.json()['results']['lv01Nm']

    return muniCd, pref, city,lv01Nm