#!/usr/bin/env python3
# -*- coding; utf-8 -*-
# Gpx2GeoDataFrame.py: GPXファイルをGeoDataFrame形式に変換する

import geopandas as gpd
import gpxpy
import shapely

def Gpx2GeoDataFrame(in_file_path, epsg=4326):

    gdf = gpd.GeoDataFrame()
    with open(f'./Log20241003-164559.gpx', 'r') as f:
        gpx = gpxpy.parse(f)

    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                gdf.loc[i, 'time'] = point.time
                gdf.loc[i, 'geometry'] = shapely.Point(point.longitude, point.latitude, point.elevation)
    gdf.crs=f'EPSG:{epsg}'
    return gdf
