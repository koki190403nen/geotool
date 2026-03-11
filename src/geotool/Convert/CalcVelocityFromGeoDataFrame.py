#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# CalcVelocityFromGeoDataFrame.py: GeoDataFrameの座標・時刻から速度を算出する
import numpy as np
import geopandas as gpd


def CalcVelocityFromGeoDataFrame(gdf, epsg=None):
    """GeoDataFrame（4次元：xyz+timestamp）から、速度を計算する

    Args:
        gdf (geopandas.GeoDataFrame): xyz + timestampを持ったGeoDataFrame. geometryはPointZ, 属性に`time`を持つ
        epsg (int): 座標系. Defaults to None.

    Returns:
        geopandas.GeoDataFrame: input(gdf)に速度列を追記
    """
    if epsg is None:
        x = gdf.geometry.x.values
        y = gdf.geometry.y.values
        z = gdf.geometry.z.values
    else:
        x = gdf.to_crs(epsg=epsg).geometry.x.values
        y = gdf.to_crs(epsg=epsg).geometry.y.values
        z = gdf.to_crs(epsg=epsg).geometry.z.values
    t = gdf['time']

    x_diff = np.diff(x, prepend=x[0])
    y_diff = np.diff(y, prepend=y[0])
    z_diff = np.diff(z, prepend=z[0])

    t_diff = (t.diff() / np.timedelta64(1, 's')).values
    v = np.where(~np.isnan(t_diff), np.sqrt(x_diff**2 + y_diff**2 + z_diff**2) / t_diff, 0)*3.6
    gdf['V[km/h]'] = v
    return gdf