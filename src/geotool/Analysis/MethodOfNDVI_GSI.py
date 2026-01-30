#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from osgeo import gdal
import cv2

# %%
class MethodOfNDVI_GSI:

    def __init__(self):
        self.thresholds={}
        pass

    def fit(self, pre_bands, post_bands, mask_img=None, lower_p=1, upper_p=99):
        """NDVI-GSI法により、人工改変箇所を抽出する

        Args:
            pre_bands (set, Array like): 改変前バンドの組み合わせ (r,g,b,nir)
            post_bands(set, Array like): 改変後バンドの組み合わせ (r,g,b,nir)
            mask_img  (Array like): マスク画像 有効部分が1, 無効部分がnp.nan
            lower_p (int): uint8変換時の下限 (%ile). Defaults to 1.
            upper_p (int): uint8変換時の上限 (%ile). Defaults to 99.
        """
        self.mask_img = np.where(mask_img==1, 1, np.nan)
        self.calc_idxes(pre_bands, post_bands)
        self.calc_binary(lower_p, upper_p)

        self.pre_vegarea   = ((self.pre_ndvi_bin==1) & (self.pre_gsi_bin==0)) .astype(np.uint8)
        self.post_barearea = ((self.post_ndvi_bin==0)& (self.post_gsi_bin==1)).astype(np.uint8)

        self.AAarea = ((self.pre_vegarea==1) & (self.post_barearea==1)).astype(np.uint8)
        return self.AAarea
        

    def calc_idxes(self, pre_bands, post_bands):
        """改変前後のNDVIとGSIを求める

        Args:
            pre_bands (set, Array like): 改変前バンドの組み合わせ (r,g,b,nir)
            post_bands(set, Array like): 改変後バンドの組み合わせ (r,g,b,nir)
        """
        r,g,b,nir=pre_bands
        self.pre_ndvi = (nir-r) / (nir+r)
        self.pre_gsi  = (r-b) / (r+g+b)

        r,g,b,nir = post_bands
        self.post_ndvi = (nir-r) / (nir+r)
        self.post_gsi  = (r-b) / (r+g+b)

    def convert_uint8(self, img, lower_p=1, upper_p=99):
        lower = np.percentile(img[~np.isnan(img)], lower_p)
        upper = np.percentile(img[~np.isnan(img)], upper_p)

        Relu_pls = lambda x:np.where(x<lower, 0, np.where(x>upper, 1, x))
        img_uint8 = (Relu_pls(img)*255).astype(np.uint8)
        return img_uint8

    def calc_binary(self, lower_p=1, upper_p=99):
        pre_ndvi_uint8 = self.convert_uint8(self.pre_ndvi, lower_p, upper_p)
        threshold, _ = cv2.threshold(pre_ndvi_uint8[self.mask_img==1], 0, 255, cv2.THRESH_OTSU)
        self.pre_ndvi_bin = (pre_ndvi_uint8>threshold).astype(np.uint8)

        post_ndvi_uint8 = self.convert_uint8(self.post_ndvi, lower_p, upper_p)
        threshold, _ = cv2.threshold(post_ndvi_uint8[self.mask_img==1], 0, 255, cv2.THRESH_OTSU)
        self.post_ndvi_bin = (post_ndvi_uint8>threshold).astype(np.uint8)

        pre_gsi_uint8 = self.convert_uint8(self.pre_gsi, lower_p, upper_p)
        threshold, _ = cv2.threshold(pre_gsi_uint8[self.mask_img==1], 0, 255, cv2.THRESH_OTSU)
        self.pre_gsi_bin = (pre_gsi_uint8>threshold).astype(np.uint8)

        post_gsi_uint8 = self.convert_uint8(self.post_gsi, lower_p, upper_p)
        threshold, _ = cv2.threshold(post_gsi_uint8[self.mask_img==1], 0, 255, cv2.THRESH_OTSU)
        self.post_gsi_bin = (post_gsi_uint8>threshold).astype(np.uint8)