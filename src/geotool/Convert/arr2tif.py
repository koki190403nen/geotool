
#!/usr/bin/env python3
# -*- cording: utf-8 -*-
# ndarray -> Geotif 変換して保存する関数

# %%
from osgeo import gdal, ogr, osr, gdal_array
import numpy as np
# %%
def arr2tif(
    arr:np.ndarray,
    out_file_path,
    geotrans=(-20, 0.05, 0, 40, 0, -0.05), projection=4326,
    ):
    """np.ndarrayをgeotiff形式で保存

    Args:
        arr (np.ndarray): データセット本体.\n
        out_file_path (str): 出力ファイルパス.\n
        geotrans (set(lon, Δlon, 0, lat, 0, -Δlat)): 左上ピクセルの座標情報\n
        projection (int or str): 座標系.int型ならEPSGコード,strならWktコード. Defaults to 4326.
    """
    
    rows, cols = arr.shape[0], arr.shape[1]
    if arr.ndim==3:
        n_bands = arr.shape[2]
    elif arr.ndim==2:
        n_bands = 1
    driver = gdal.GetDriverByName('GTiff')
    gdal_type = gdal_array.NumericTypeCodeToGDALTypeCode(arr.dtype)  # numpy.dtype をgdal.DataTypeに変換
    outRaster = driver.Create(out_file_path, cols, rows, n_bands, gdal_type)
    outRaster.SetGeoTransform(geotrans)

    if arr.ndim==2:
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray(arr)
    elif arr.ndim==3:
        for i in range(arr.shape[2]):
            outband = outRaster.GetRasterBand(i+1)
            outband.WriteArray(arr[:,:,i])

    # projectionがEPSGコードだった場合の処理
    if type(projection) is int:
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(projection)
        projection = outRasterSRS.ExportToWkt()
    outRaster.SetProjection(projection)
    outband.FlushCache()
    del outRaster