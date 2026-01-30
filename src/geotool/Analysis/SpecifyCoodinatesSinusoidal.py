#!/usr/bin/env python3
# -*- cooding: utf-8 -*-
# SpecifyCoodinatesSinusoidal.py : サンソン図法の緯度経度をもとに写真座標を求める
# %% 指定した緯度経度のピクセルの図形座標を求める
import numpy as np
def SpecifyCoodinatesSinusoidal(lon, lat, lon_0=0, tile_h=29, tile_w=5, pixel=2400, int_return=True):

    """ Calc img projection with Sinusoidal

    Args:
        lon     (float)     : 経度
        lat     (float)     : 緯度
        lon_0   (float)     : 本初子午線の経度  (Default to: 0)
        tile_h  (int)       : タイル番号(h)  (Default to: 29)
        tile_w  (int)       : タイル番号(w)  (Default to: 5)
        pixel   (int)       : タイルの一辺当たりのピクセル数  (Default to: 2400)
        int_return (bool)   : 返り値をintにするかどうか  (Default to: True)

    Returns:
        row     (int)       : 画像座標の行番号(0始まり)
        column  (int)       : 画像座標の列番号(0始まり)
    """

    world_x = 0.5 + (lon - lon_0)/360 * np.cos(np.radians(lat))
    world_y = lat / 180 - 0.5

    row = (np.abs(world_y /(1/18)) - tile_w) * pixel
    column = (np.abs(world_x /(1/36)) - tile_h) * pixel

    if int_return:
        row = int(row)
        column = int(column)

    return row, column

def calc_img_proj_epsg4326(
        lon, lat,
        geotrans=(-180, 0.05, 0, 90, 0, -0.05)
    ):

    """Calc img projection with epsg4326

    Args:
        lon     (int)   : 経度
        lat     (int)   : 緯度

    Returns:
        img_y   (int)   : 画像座標 (y座標, 0始まり)
        img_x   (int)   : 画像座標 (x座標, 0始まり)
    """

    img_x = int((lon*20 - geotrans[0]*20) // (geotrans[1]*20))
    img_y = int((lat*20 - geotrans[3]*20) // (geotrans[5]*20))

    return img_y, img_x