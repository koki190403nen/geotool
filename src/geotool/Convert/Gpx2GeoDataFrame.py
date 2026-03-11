#!/usr/bin/env python3
# -*- coding; utf-8 -*-
# Gpx2GeoDataFrame.py: GPXファイルをGeoDataFrame形式に変換する

import geopandas as gpd
import gpxpy
import shapely

def Gpx2GeoDataFrame(src_path, epsg=4326):
    """GPXファイルをGeoDataFrame形式に変換する

    Args:
        src_path (str, path): 変換元gpxファイルパス
        epsg (int)          : 座標系(epsg). Defaults to 4326.

    Returns:
        geopandas.GeoDataFrame: gpxを変換したGeoDataFrame.
    """

    gdf = gpd.GeoDataFrame()
    with open(src_path, 'r') as f:
        gpx = gpxpy.parse(f)

    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                gdf.loc[i, 'time'] = point.time
                gdf.loc[i, 'geometry'] = shapely.Point(point.longitude, point.latitude, point.elevation)
    gdf.crs=f'EPSG:{epsg}'
    return gdf
