# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

# %%
class Raster2Arr:
    def __init__(self):
        self.VZI    = None
        self.SPI3   = None
        self.mR95pT = None
        self.NDVI   = None

        self.h      = 1600
        self.w      = 1500
    
    def fit(self, row, col, date_arr):
        
        self.capture_VZI(row, col, date_arr)
        self.capture_SPI3(row, col, date_arr)
        self.capture_mR95pT(row, col, date_arr)
        self.capture_NDVI(row, col, date_arr)
        return self

    def capture_VZI(self, row, col, date_arr):
        print('Initializing capture VZI...')
        VZI_ls  = []
        for date in date_arr:
            get_img = np.fromfile(
                f'D:/ResearchData3/Level4/MOD16days/VZI/VZI.A{date.strftime("%Y%j")}.float32_h1600w1500.raw',
                count=self.h*self.w, dtype=np.float32
            ).reshape(self.h, self.w)

            VZI_ls.append(get_img[row, col])

        self.VZI = np.array(VZI_ls)
    
    def capture_SPI3(self, row, col, date_arr):
        print('Initializing capture SPI3...')
        SPI_ls  = []
        for date in date_arr:
            get_img = np.fromfile(
                f'D:/ResearchData3/Level4/MOD16days/SPI3/SPI3.A{date.strftime("%Y%j")}.float32_h1600w1500.raw',
                count=self.h*self.w, dtype=np.float32
            ).reshape(self.h,self.w)

            SPI_ls.append(get_img[row, col])
        self.SPI3 = np.array(SPI_ls)

    def capture_mR95pT(self, row, col, date_arr):
        print('Initializing capture mR95pT...')
        mR95pT_ls  = []
        for date in date_arr:
            get_img = np.fromfile(
                f'D:/ResearchData3/Level4/MOD16days/CCIs/mR95pT/mR95pT.A{date.strftime("%Y%j")}.float64_h1600w1500.raw',
                count=self.h*self.w, dtype=np.float32
            ).reshape(self.h,self.w).astype(np.float32)
            mR95pT_ls.append(get_img[row, col])
        self.mR95pT = np.array(mR95pT_ls)
        
    def capture_NDVI(self, row, col, date_arr):
        print('Initializing capture NDVI...')
        NDVI_ls  = []
        for date in date_arr:
            get_img = np.fromfile(
                f'D:/ResearchData3/Level3/MOD13C1/MOD13C1.A{date.strftime("%Y%j")}.int16_h1600w1500.raw',
                count=self.h*self.w, dtype=np.int16
            ).reshape(self.h,self.w).astype(np.float32)

            NDVI_ls.append(get_img[row, col])
        self.NDVI = np.array(NDVI_ls)
