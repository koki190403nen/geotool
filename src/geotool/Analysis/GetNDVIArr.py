# %%
import numpy as np
import pandas as pd
from .SpecifyCoodinatesSinusoidal import SpecifyCoodinatesSinusoidal as scs


# %%
class GetNDVIArr:
    def __init__(self, h=2400, w=2400):
        self.h, self.w = h, w
        self.get_all_data()
    
    # 画像データセットの読込
    def get_all_data(self):
        self.all_ndvi_img = np.full((self.h,self.w,21*23), np.nan, dtype=np.int16)
        c=0
        for year in np.arange(2001, 2021+1):
            for doy in np.arange(1, 366, 16):
                get_img = np.fromfile(
                    f'D:/ResearchData2/Level3/MOD13A1_JA/MOD13A1_JA_RAW_500m/MOD13A1.A{year}{str(doy).zfill(3)}.int16_h{self.h}w{self.w}.raw',
                    count=self.h*self.w, dtype=np.int16
                ).reshape(self.h,self.w)
                self.all_ndvi_img[:,:,c] = get_img
                c+=1
            print(year)

    # 緯度経度と画像座標の計算
    def get_proj(self, area_name):
        area_df = pd.read_csv(f'D:/ResearchData2/LevelExtra/TargetArea.csv')

        self.lat = area_df.query(f'Name=="{area_name}"')['Lat'].values[0]
        self.lon = area_df.query(f'Name=="{area_name}"')['Lon'].values[0]
        self.img_y, self.img_x = scs(lat=self.lat, lon=self.lon)
        return self.img_y, self.img_x
    
    # 指定地点のndviデータを抽出
    def sampling_1point(self, area_name):
        self.get_proj(area_name)
        ndvi_arr = self.all_ndvi_img[self.img_y, self.img_x, :].astype(np.float32)
        return ndvi_arr
# %%
