#!/usr/bin/env python-3
# -*- coding: utf-8 -*-
# AdjustSizeOfImages.py: 2枚以上の入力された画像の、切り抜き範囲・ピクセル数をそろえる

# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from osgeo import gdal, osr
import geopandas as gpd
import cv2, glob, os
from shapely.geometry import Polygon

if __name__=='__main__':
    from ..Convert import arr2tif, geotrans2extent
else:
    from geotool.Convert import arr2tif, geotrans2extent

# %%
class AdjustSizeOfImages:
    def __init__(self):
        """2枚以上の画像の範囲・解像度をそろえる関数

        Attributes:
            self.boundary_gdf (geopandas.GeoDataFrame): 入力したラスター画像の重畳部分（ポリゴン）
            self.boundary_extents (list: extents): 入力したラスター画像の重畳部分（extents）
            self.shapes (list: [h,w]): 入力したラスター画像の重畳部分の画像サイズ([h,w])
        """
        self.boundary_gdf       = gpd.GeoDataFrame() 
        self.boundary_extents   = []
        self.shapes             = []

    def fit(self, src_pathes, dst_pathes, kernel=cv2.INTER_CUBIC):
        """fit関数

        Args:
            src_pathes (_type_)         : 入力するラスター画像のパスのリスト
            dst_pathes (_type_)         : 出力するラスター画像のパスのリスト
            kernel (_type_, optional)   : リサイズに使うカーネル

        Returns:
            _type_: _description_
        """
        
        self.calc_boundary(src_pathes)
        self.convert_imgs(src_pathes, dst_pathes, kernel=kernel)
        return self
        
    def calc_boundary(self, src_pathes):
        """入力したラスター画像の重複部分を囲うboundaryを作成する

        Args:
            src_pathes (list[str]): 入力するラスター画像のパスのリスト
        """

        extents = []
        epsgs   = []
        for path in src_pathes:
            src = gdal.Open(path)
            h,w = [src.ReadAsArray().shape[i] for i in [-2,-1]]
            self.shapes.append([h,w])
            extents.append(geotrans2extent(src.GetGeoTransform(), h,w))

            srs = osr.SpatialReference()
            srs.ImportFromWkt(src.GetProjection())
            epsgs.append(srs.GetAuthorityCode(None))
            del src, srs

        if len(np.unique(epsgs))!=1:
            print('入力する座標系をそろえてください')
            return epsgs

        extents = np.array(extents)
        self.boundary_extents = [np.nanmax(extents[:,0]),np.nanmin(extents[:,1]),np.nanmax(extents[:,2]),np.nanmin(extents[:,3])]
        self.boundary_gdf = gpd.GeoDataFrame()
        self.boundary_gdf.geometry = np.array([Polygon([(self.boundary_extents[0], self.boundary_extents[2]), (self.boundary_extents[0], self.boundary_extents[3]), (self.boundary_extents[1], self.boundary_extents[3]), (self.boundary_extents[1], self.boundary_extents[2])])])
        self.boundary_gdf.set_crs(epsg=epsgs[0])

        return self
    
    def convert_imgs(self, src_pathes, dst_pathes, kernel = cv2.INTER_CUBIC):
        """算出したboundaryをもとに切り出し、リサイズを行う

        Args:
            src_pathes (str: path)  : 入力するラスター画像のパスのリスト
            dst_pathes (str: path)  : 出力するラスター画像のパスのリスト
            kernel(cv2.INTER_XX)    : リサイズに使うカーネル
        """
        os.makedirs('./working/', exist_ok=True)

        for src_path, dst_path in zip(src_pathes, dst_pathes):
            gdal.Warp(
                srcDSOrSrcDSTab  = src_path,
                destNameOrDestDS = f'./working/working.tif',
                outputBounds     = [self.boundary_extents[i] for i in [0,2,1,3]]
            )
            out_shapes = np.nanmin(np.array(self.shapes), axis=0)
            working_src = gdal.Open(f'./working/working.tif')
            working_img = working_src.ReadAsArray()
            if working_img.ndim==3:
                out_img_ls = []
                for c in range(working_img.shape[0]):
                    out_img_ls.append(cv2.resize(working_img[c,:,:], dsize=list(out_shapes), interpolation=kernel))
                out_img = np.array(out_img_ls).transpose((1,2,0))
            elif working_img.ndim==2:
                out_img = cv2.resize(working_img, dsize=list(out_shapes), interpolation=kernel)
            
            #return working_src.GetGeoTransform()
            arr2tif(out_img, dst_path, geotrans=working_src.GetGeoTransform(), projection=working_src.GetProjection())

        return self

if __name__=="__main__":
    src_pathes = glob.glob(f'./02_DATA/01_ORG/*.tif') + glob.glob(f'./02_DATA/01_ORG/*.geotif')
    dst_pathes = [f'./02_DATA/02_Resized/{os.path.basename(path).split(".")[0]}_Resized.tif' for path in src_pathes]
    
    asoi = AdjustSizeOfImages()
    asoi.fit(src_pathes, dst_pathes)
