# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from osgeo import gdal, osr
import geopandas as gpd
import cv2, glob, os

if __name__== '__main__':
    from Convert import arr2tif, vec2ras
else:
    from ..Convert import arr2tif, vec2ras

# %%
class NDVI_GSI_Binarization:
    def __init__(self):
        """入力した画像をもとに、NDVI, GSI, NDVI二値化画像, GSI二値化画像を作成する
        Attributes:
            sat_src: 入力した衛星画像のSRCデータ
            sat_img: 入力した衛星画像のimgデータ
            ndvi_img: NDVI画像. (-1 ~ 1)
            gsi_img: GSI画像. (-1 ~ 1)
            target_datasets : 閾値計算に用いたデータセット. (fit関数を実行した場合はNDVI, GSIの順で保存)
            thresholds      : 求めた閾値. (fit関数を実行した場合はNDVI, GSIの順で保存)
        
        """

        os.makedirs('./working/', exist_ok=True)
        self.ndvi_img = None
        self.gsi_img  = None
        self.datasets = []
        self.thresholds = []

    def fit(
            self,
            src_sat_path,
            dst_ndvi_path=None, dst_gsi_path=None, dst_ndvi_bin_path=None, dst_gsi_bin_path=None,
            band_composition=[], teacher=None, hist=False, hist_title=None
            ):
        """fit関数

        Args:
            src_sat_path (str: path, geotiff)       : 入力するマルチバンド衛星画像のパス
            dst_ndvi_path (str: path, geotiff)      : 出力するNDVI画像のパス Defaults to None.
            dst_gsi_path (str: path, geotiff)       : 出力するGSI画像のパス. Defaults to None.
            dst_ndvi_bin_path (str: path, geotiff)  : 出力するNDVI二値化画像のパス. Defaults to None.
            dst_gsi_bin_path (str: path, geotiff))  : 出力するGSI二値化画像のパス. Defaults to None.
            band_composition (list, optional)       : 各波長帯が保存されているチャンネル番号. 0スタート.. Defaults to [].
            teacher (str:path,vector or list[int,int], optional)  : 閾値決定のための教師情報。パスが入力された場合はベクター範囲の画像から自動算出される. Defaults to None.
            hist (bool, optional)                   : 二値化時の閾値を可視化するための設定.
            hist_title (str)                        : ヒストグラムのタイトル

        Returns:
            _type_: _description_
        """

        self.calc_ndvi_gsi(src_sat_path=src_sat_path, band_composition=band_composition)

        if type(teacher)==str:
            self.extraction_teacher_mask(teacher_vector_path=teacher)
            ndvi_threshold = self.calc_threshold(src_img=self.ndvi_img, hist=hist, title=f'NDVI（{hist_title}）')
            gsi_threshold  = self.calc_threshold(src_img=self.gsi_img,  hist=hist, title=f'GSI（{hist_title}）')
        else:
            ndvi_threshold, gsi_threshold = teacher
        
        self.ndvi_bin_img = (self.ndvi_img >= ndvi_threshold).astype(np.uint8)
        self.gsi_bin_img  = (self.gsi_img  >= gsi_threshold ).astype(np.uint8)

        for img, path in zip((self.ndvi_img, self.gsi_img, self.ndvi_bin_img, self.gsi_bin_img), (dst_ndvi_path, dst_gsi_path, dst_ndvi_bin_path, dst_gsi_bin_path)):
            arr2tif(img, path, geotrans=self.sat_src.GetGeoTransform(), projection=self.sat_src.GetProjection())

        self.sat_src  # geotiffの開放
        return self
        
            

        

    def calc_ndvi_gsi(self, src_sat_path, band_composition=[]):
        """NDVIとGSIを計算する

        Args:
            src_sat_path (str: path, geotiff): 入力するマルチバンド衛星画像のパス
            band_composition (list [R,G,B,NIR]): 各波長帯が保存されているチャンネル番号. 0スタート.

        Returns:
            _type_: _description_
        """
        self.sat_src = gdal.Open(src_sat_path)
        self.sat_img = self.sat_src.ReadAsArray().astype(np.float32)
        R,G,B,NIR = band_composition
        self.ndvi_img = (self.sat_img[NIR,:,:] - self.sat_img[R,:,:]) / (self.sat_img[NIR,:,:] + self.sat_img[R,:,:])
        self.gsi_img  = (self.sat_img[R,:,:] - self.sat_img[B,:,:]) / (self.sat_img[R,:,:]+self.sat_img[G,:,:]+self.sat_img[B,:,:])
        return self

    def extraction_teacher_mask(self, teacher_vector_path):
        # sat_srcのepgsコードを確認
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.sat_src.GetProjection())
        sat_epsg = srs.GetAuthorityCode(None)

        teacher_gdf = gpd.read_file(teacher_vector_path).to_crs(epsg=sat_epsg)
        teacher_gdf['DN'] = 1
        teacher_gdf.to_file('./working/working.geojson')
        del teacher_gdf

        vec2ras(
            in_vector_path = './working/working.geojson',
            out_raster_path = './working/working.tif',
            attribute = 'DN',
            geotrans = self.sat_src.GetGeoTransform(),
            cols = self.sat_src.ReadAsArray().shape[-1],
            rows = self.sat_src.ReadAsArray().shape[-2],
            nodata = -1,
            dtype = np.int16
        )
        self.teacher_mask_img = gdal.Open(f'./working/working.tif').ReadAsArray()

        return self
    
    def calc_threshold(self, src_img, hist=False, title=None):
        """入力した画像からマスク画像を用いて閾値を求める

        Args:
            src_img (_type_): _description_
            hist (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        target_dataset_float = src_img[self.teacher_mask_img==1]

        self.datasets.append(target_dataset_float)
        
        # 大津の二値化
        target_dataset_int   = ((target_dataset_float - np.nanmin(target_dataset_float)) / (np.nanmax(target_dataset_float) - np.nanmin(target_dataset_float))  * 255).astype(np.uint8)
        thresh_int, _ = cv2.threshold(target_dataset_int, 0, 255, cv2.THRESH_OTSU)
        thresh = thresh_int/255 * (np.nanmax(target_dataset_float) - np.nanmin(target_dataset_float)) + np.nanmin(target_dataset_float)

        
        self.thresholds.append(thresh)
        if hist:
            plt.rcParams['font.family'] = 'Meiryo'
            plt.hist(target_dataset_float, bins=200)
            ylim = plt.ylim()
            plt.vlines(thresh, *ylim, colors='red', label=f'閾値={thresh:.2f}')
            plt.title(title)
            plt.legend()
            plt.ylim(*ylim)
            plt.show()
        return thresh

if __name__=='__main__':


    ngb = NDVI_GSI_Binarization()
    ngb.fit(
        src_sat_path        = './02_DATA/02_Resized/25JAN22020728-M2AS-200009817770_01_P001_Resized.tif',
        dst_ndvi_path       = './02_DATA/03_IndexImage/NDVI.tif',
        dst_gsi_path        = './02_DATA/03_IndexImage/GSI.tif',
        dst_ndvi_bin_path   = './02_DATA/04_BinaryImage/NDVI_bin.tif',
        dst_gsi_bin_path    = './02_DATA/04_BinaryImage/GSI_bin.tif',
        band_composition    = [4,2,1,6],
        teacher             = './02_DATA/00_Params/TeacherData.geojson',
        hist                = True
    )
