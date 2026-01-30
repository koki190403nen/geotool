#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# CalcVelocityFromGeoDataFrame.py: GeoDataFrameの座標・時刻から速度を算出する
import numpy as np
import geopandas as gpd


def CalcVelocityFromGeoDataFrame(gdf, epsg=6677):

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