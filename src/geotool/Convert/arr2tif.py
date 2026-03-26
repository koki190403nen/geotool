
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ndarray -> Geotif 変換して保存する関数

# %%
import os
from osgeo import gdal, osr, gdal_array
import numpy as np
# %%
def arr2tif(
    arr: np.ndarray,
    out_file_path: str | os.PathLike,
    geotrans: tuple[float, ...] = (-20, 0.05, 0, 40, 0, -0.05),
    projection: int | str = 4326,
    band_descriptions: list[str] | dict[int, str] | None = None,
    ) -> None:
    """np.ndarrayをgeotiff形式で保存

    Args:
        arr (np.ndarray): データセット本体.
        out_file_path (str | os.PathLike): 出力ファイルパス.
        geotrans (tuple[float, ...]): 左上ピクセルの座標情報 (lon, Δlon, 0, lat, 0, -Δlat).
        projection (int | str): 座標系.int型ならEPSGコード,strならWktコード. Defaults to 4326.
        band_descriptions (list[str] | dict[int, str] | None): バンドの説明.
            list の場合はインデックス順に設定（リスト長がバンド数より短い場合は該当バンドのみ設定）.
            dict の場合はキーをバンド番号（1始まり）として設定.
            None の場合は何もしない. Defaults to None.
    """
    # arrが2D or 3Dかチェック
    if arr.ndim not in (2, 3):
        raise ValueError(f"arr must be 2D or 3D, got {arr.ndim}D")

    # バンド数を取得
    rows, cols = arr.shape[:2]
    if arr.ndim == 3:
        n_bands = arr.shape[2]
    elif arr.ndim == 2:
        n_bands = 1

    # 書き込むためのラスターファイルを作成
    driver = gdal.GetDriverByName('GTiff')
    gdal_type = gdal_array.NumericTypeCodeToGDALTypeCode(arr.dtype)  # numpy.dtype をgdal.DataTypeに変換
    outRaster = driver.Create(out_file_path, cols, rows, n_bands, gdal_type)
    if outRaster is None:
        raise RuntimeError(f"Failed to create GeoTIFF: {out_file_path}")
    outRaster.SetGeoTransform(geotrans)

    # arrが2次元の場合は3次元に変更。3次元の場合はそのまま
    if arr.ndim == 2:
        _arr = arr[..., np.newaxis]
    else:
        _arr = arr

    # 作成したラスターファイルにデータを書き込み
    for i in range(n_bands):
        outband = outRaster.GetRasterBand(i + 1)
        outband.WriteArray(_arr[:, :, i])
        # descriptionsがある場合は、追記する
        if band_descriptions is not None:
            if isinstance(band_descriptions, list) and i < len(band_descriptions):
                outband.SetDescription(band_descriptions[i])
            elif isinstance(band_descriptions, dict) and (i + 1) in band_descriptions:
                outband.SetDescription(band_descriptions[i + 1])

    # projectionがEPSGコードだった場合の処理
    if isinstance(projection, (int, np.integer)):
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(projection)
        projection = outRasterSRS.ExportToWkt()
    outRaster.SetProjection(projection)
    outRaster.FlushCache()
    outRaster = None
