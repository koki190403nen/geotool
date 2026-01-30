#/usr/bin/env python3
# -*- coding: utf-8 -*-
# Extract_1pint_items: 指定したlon latの観測情報をcsvにまとめる
# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
# %%

def Extract_1point_items(lat, lon, area_name, sample_dir_path='./sample/dataset/africa_csv/', lulc=None):

    h,w = 1600, 1500
    ai_img = np.fromfile(
        f'D:/ResearchData3/LevelExtra/RAW/AIKoppen.C19912020.float32_h1600w1500.raw',
        dtype=np.float32
    ).reshape(h,w)
    lulc_img = np.fromfile(
        f'D:/ResearchData3/Level3/MCD12C1/MCD12C1.A2010001.uint8_h1600w1500.raw',
        dtype=np.uint8
    ).reshape(h,w)
    date_arr = pd.to_datetime(
        [f'{year}/{doy}' for year in range(2001, 2020+1) for doy in range(1, 366, 16)],
        format='%Y/%j')
    srs_df = pd.read_csv(f'{sample_dir_path}/srs.csv', index_col=0)  # 座標系の記録


    row, col = int((40-lat)/0.05), int((-20-lon) / (-0.05))  # 画像座標に変換s

    meta_dict = {'SPI3': ['SPI3',           'float32'],
             'mR95pT'  : ['ccis/mR95pT',    'float64'],
             'PRCPTOT' : ['ccis/PRCPTOT',   'float64'],
             'NDVI_Smoothed' : ['NDVI_Smoothed',  'float64'],
             'VZI'     : ['VZI',            'float32'],
             'STI'     : ['STI',            'float32'],
             'PAR'     : ['PAR/JASMES',     'float32'],
             'MeanTEMP': ['TEMP/MeanTEMP',  'float32'],
             'PARRZ'   : ['PARRZ',          'float32']
             }
    out_df = pd.DataFrame(columns=meta_dict.keys())


    for key, (dir, dtype) in meta_dict.items():
        for i, date in enumerate(date_arr):
            get_img = np.fromfile(
                f'D:/ResearchData3/Level4/MOD16days/{dir}/{key}.A{date.strftime("%Y%j")}.{dtype}_h1600w1500.raw',
                count=h*w, dtype=dtype
            ).reshape(h,w)

            get_val = get_img[row, col]
            out_df.loc[date.strftime("%Y/%m/%d"), key] = get_val

        print(key)
    
    out_df['NDVI'] = out_df['NDVI_Smoothed']/10000

    srs_df.loc[area_name, ['lat', 'lon', 'LULC']] = lat, lon, lulc
    srs_df.loc[area_name,['LULC_code', 'KoppenAI']] = lulc_img[row, col], ai_img[row, col]
    srs_df.to_csv(f'{sample_dir_path}/srs.csv')
    out_df.to_csv(f'{sample_dir_path}/{area_name}.csv')
    print(f'Export {area_name}.csv')

    return out_df