#!/usr/bin/env python-3
# -*- coding: utf-8 -*-
# ras2vec.py: ラスターデータをベクターに変換する

import os
from osgeo import gdal, ogr, osr
def ras2vec(input_path=None, output_path=None, gdal_src=None):
    if os.path.exists(output_path):
        os.remove(output_path)
    if input_path is not None:
        src = gdal.Open(input_path)
    elif gdal_src is not None:
        src = gdal_src

    src_band = src.GetRasterBand(1)
    dst_driver = ogr.GetDriverByName('GeoJSON')
    src_ref = src.GetProjection()

    dst_ref = osr.SpatialReference()
    dst_ref.ImportFromWkt(src_ref)

    dst_ds = dst_driver.CreateDataSource(output_path)
    dst_layer = dst_ds.CreateLayer('DN', srs=dst_ref)

    fld = ogr.FieldDefn('DN', ogr.OFTInteger)
    dst_layer.CreateField(fld)
    dst_filed = dst_layer.GetLayerDefn().GetFieldIndex('DN')
    gdal.Polygonize(src_band, None, dst_layer, dst_filed, [], callback=None)

    del src, dst_ds