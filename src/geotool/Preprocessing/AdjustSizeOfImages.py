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
    import sys
    sys.path.append('../')
    from ..Convert.arr2tif import arr2tif
else:
    from geotool.Convert import arr2tif, geotrans2extent

# %%
class AdjustSizeOfImages:
    def __init__(self):
        """2枚以上の画像の範囲・解像度をそろえる関数

        Attributes:
            self.boundary_gdf (geopandas.GeoDataFrame): 入力したラスター画像の重畳部分（ポリゴン）
            self.boundary_extents (list: extents): 入力したラスター画像の重畳部分（extents）
            self.out_imgs (list: img(Array like)): リサイズした画像(np.ndarray)
            self.src (list: gdal.Dataset): 出力する画像のヘッダ情報
        """
        self.boundary_gdf       = gpd.GeoDataFrame() 
        self.boundary_extents   = []

    def fit(self, src_pathes, dst_pathes=None, aoi_path=None, kernel=cv2.INTER_CUBIC, mode='downscale', epsg=None):
        """fit関数

        Args:
            src_pathes (list[path:str])     : 入力するラスター画像のパスのリスト
            dst_pathes (list[path:str])     : 出力するラスター画像のパスのリスト. Noneの時には画像を変数として保持する
            aoi_path (path:str)             : AOI(ベクター形式)のパス
            kernel (_type_, optional)       : リサイズに使うカーネル
            mode(str, downscale or upscale) : 高解像度化と低解像度化の指定. defaults to downscale
            epsg (int)              : 出力先のEPSGコード

        Returns:
            _type_: _description_
        """
        
        boundary_res = self.calc_boundary(src_pathes, aoi_path=aoi_path, epsg=epsg)
        if boundary_res=='error':
            return
        self.clip(src_pathes, epsg=epsg)
        self.calc_out_src(mode=mode)

        if dst_pathes is None:
            self.resize(kernel=kernel)
        else:
            self.resize_output(dst_pathes=dst_pathes, kernel=kernel)


        return self
        
    def calc_boundary(self, src_pathes, aoi_path=None, epsg=None):
        """入力したラスター画像の重複部分を囲うboundaryを作成する

        Args:
            src_pathes (list[str]): 入力するラスター画像のパスのリスト
        """

        extents = []
        epsgs   = []
        for path in src_pathes:
            src = gdal.Open(path)
            h = src.RasterYSize
            w = src.RasterXSize
            extents.append(geotrans2extent(src.GetGeoTransform(), h,w))

            srs = osr.SpatialReference()
            srs.ImportFromWkt(src.GetProjection())
            epsgs.append(srs.GetAuthorityCode(None))
            del src, srs

        if (len(np.unique(epsgs))>1) & (epsg is None):
            print('入力する座標系をそろえてください. もしくはepsgコードを入力してください')
            return 'error'

        extents = np.array(extents)
        self.boundary_extents = [np.nanmax(extents[:,0]),np.nanmin(extents[:,1]),np.nanmax(extents[:,2]),np.nanmin(extents[:,3])]

        # AOIが入力された時の処理
        if aoi_path is not None:
            AOI_gdf = gpd.read_file(aoi_path).to_crs(epsg=int(epsgs[0]))
            AOI_Xs  = np.array([i for i in AOI_gdf.geometry.values[0].exterior.coords])[:,0]
            AOI_Ys  = np.array([i for i in AOI_gdf.geometry.values[0].exterior.coords])[:,1]
            AOI_boundary_extents  = [np.nanmin(AOI_Xs), np.nanmax(AOI_Xs), np.nanmin(AOI_Ys), np.nanmax(AOI_Ys)]
            self.boundary_extents = [
                np.nanmax([self.boundary_extents[0], AOI_boundary_extents[0]]),
                np.nanmin([self.boundary_extents[1], AOI_boundary_extents[1]]),
                np.nanmax([self.boundary_extents[2], AOI_boundary_extents[2]]),
                np.nanmin([self.boundary_extents[3], AOI_boundary_extents[3]])
                ]

        self.boundary_gdf = gpd.GeoDataFrame()
        self.boundary_gdf.geometry = np.array([Polygon([(self.boundary_extents[0], self.boundary_extents[2]), (self.boundary_extents[0], self.boundary_extents[3]), (self.boundary_extents[1], self.boundary_extents[3]), (self.boundary_extents[1], self.boundary_extents[2])])])
        self.boundary_gdf.set_crs(epsg=epsgs[0])

        return self
    
    def clip(self, src_pathes, epsg=None):
        """算出したboundaryをもとに切り出し、リサイズを行う

        Args:
            src_pathes (str: path)  : 入力するラスター画像のパスのリスト
            epsg (int)              : 出力先のEPSGコード
            mode (str, downscale or upscale): 解像度をどちらに合わせるのかを指定する
        """
        os.makedirs('./working/', exist_ok=True)
        self.working_srcs = []
        # 同じboudingで区切る
        for i, src_path in enumerate(src_pathes):
            if epsg is None:
                gdal.Warp(
                    srcDSOrSrcDSTab  = src_path,
                    destNameOrDestDS = f'./working/working{i}.tif',
                    outputBounds     = [self.boundary_extents[i] for i in [0,2,1,3]]
            )
            else:
                gdal.Warp(
                    srcDSOrSrcDSTab  = src_path,
                    destNameOrDestDS = f'./working/working{i}.tif',
                    outputBounds     = [self.boundary_extents[i] for i in [0,2,1,3]],
                    dstSRS           = f'EPSG:{epsg}'
            )
            self.working_srcs.append(gdal.Open(f'./working/working{i}.tif'))
        return self
    
    def calc_out_src(self, mode='downscale'):

        # shapeとgeotransを確定する
        working_shapes = np.array([[working_src.RasterYSize, working_src.RasterXSize] for working_src in self.working_srcs])
        working_pixels = np.array([[working_src.RasterYSize*working_src.RasterXSize] for working_src in  self.working_srcs])
        if mode=='downscale':
            self.out_shape = working_shapes[np.argmin(working_pixels)]
            self.out_src   = self.working_srcs[np.argmin(working_pixels)]

        elif mode=='upscale':
            self.out_shape = working_shapes[np.argmax(working_pixels)]
            self.out_src   = self.working_srcs[np.argmax(working_pixels)]
        
        else:
            print('mode has been input "downscale" or "upscale"')
            return
        
        return self
    
    def resize(self, kernel=cv2.INTER_CUBIC):
        
        # 画像本体をリサイズし、クラス内変数に保持する。
        self.out_imgs = []
        for i, working_src in enumerate(self.working_srcs):

            working_img = working_src.ReadAsArray()
            if working_img.ndim==2:
                self.out_imgs.append(cv2.resize(working_img, dsize=self.out_shape[::-1], interpolation=kernel))
            elif working_img.ndim==3:
                append_img_ls = []
                for c in range(working_img.shape[0]):
                    append_img_ls.append(cv2.resize(working_img[c,:,:], dsize=self.out_shape[::-1], interpolation=kernel))
                self.out_imgs.append(np.array(append_img_ls))
                del append_img_ls
                
        return self
    
    def resize_output(self, dst_pathes, kernel=cv2.INTER_CUBIC):
        for i, (working_src, dst_path) in enumerate(zip(self.working_srcs, dst_pathes)):
            working_img = working_src.ReadAsArray()
            if working_img.ndim==2:
                out_img = cv2.resize(working_img, dsize=self.out_shape[::-1], interpolation=kernel)
            elif working_img.ndim==3:
                out_imgs=[]
                for c in range(working_img.shape[0]):
                    out_imgs.append(cv2.resize(working_img[c,:,:], dsize=self.out_shape[::-1], interpolation=kernel))
                out_img = np.array(out_imgs).transpose((1,2,0))
                del out_imgs
            
            arr2tif(out_img, dst_path, geotrans=self.out_src.GetGeoTransform(), projection=self.out_src.GetProjection())
        
        return self



if __name__=="__main__":
    src_pathes = glob.glob(f'../../02_DATA/01_ORG/*.tif') + glob.glob(f'../../02_DATA/01_ORG/*.geotif')
    dst_pathes = [f'./02_DATA/02_Resized/{os.path.basename(path).split(".")[0]}_Resized.tif' for path in src_pathes]
    
    asoi = AdjustSizeOfImages()
    asoi.fit(src_pathes, dst_pathes)
