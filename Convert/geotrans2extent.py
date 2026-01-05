#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# geotrans2extent.py: geotransからmatplotlib引数に使用可能なextentに変換する
from osgeo import gdal

def geotrans2extent(geotrans=None, h=None, w=None, path=None):
    """gdal GeoTransformを matplotlib extent形式に変換する

    Args:
        geotrans (_type_, optional): _description_. Defaults to None.
        h (_type_, optional): _description_. Defaults to None.
        w (_type_, optional): _description_. Defaults to None.
        path (_type_, optional): _description_. Defaults to None.

    Returns:
        extent: (x_min, x_max, y_min, y_max)
    """

    if path is not None:
        src = gdal.Open(path)
        geotrans = src.GetGeoTransform()
        shape = src.ReadAsArray().shape
        h,w = shape[0], shape[1]
        print(h,w)
        del src
        return geotrans2extent(geotrans, h, w)
    x_min, x_d, _, y_max, _, y_d = geotrans
    x_max, y_min = x_min + w*x_d, y_max + h*y_d
    extent = (x_min, x_max, y_min, y_max)
    return extent