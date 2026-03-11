#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# judge_crow.py: カラスがいるかどうか判定する

# %%
import numpy as np
import glob
import cv2
import threading
import datetime
import pandas as pd
import warnings
warnings.simplefilter('ignore')
if __name__=='__main__':
    from calc_sinh import calc_sinh
else:
    from . import calc_sinh

# %% 
def get_circle_img(dir_path='E:/ResearchData4/Level1/circle_img/', degree_ls = [75]):
    """サークル画像を入手する

    Args:
        dir_path (str, optional): サークル画像が保存されたディレクトリパス.
        degree_ls (list, optional): サークル画像の開口度. Defaults to [75].

    Returns:
        circle_img_dict (dictionary, Array like)    : サークル画像
        circle_area_dict (dictionary, int)          : サークル画像の面積
    """
    
    circle_dict = {}
    for degree in degree_ls:
        file_path = f'{dir_path}/Mask{degree}circle.tif'
        circle_3d = cv2.imread(file_path)
        circle_2d = np.where(circle_3d[:,:,0]==0, np.nan, 1).astype(np.float32)
        circle_dict[degree] = [
            circle_2d,
            np.nansum(~np.isnan(circle_2d))
            ]
    return circle_dict

# %%
class ProcessWsiImage(threading.Thread):
    """BI値を計算する

    """

    def __init__(self, wsi_path=None, masking=True, circle_dict=None, threshold_area=0.95):
        """RGB画像からBI画像を作成する
        しきい値を設定することでカラス抜き画像や白飛び抜き画像を作成する

        Args:
            wsi_path (str, optional): 処理を行う全天画像. Defaults to None.
            masking (bool): マスキングを実行するかどうか
            circle_dict (dict): サークル画像のディクショナリ
            threshold_area (float): 使用可能となる画素の面積

        Attributes:
            .wsi_path (str)                         : 全天画像のパス
            .wsi_3d (Array like (3d, uint8))        : 使用する全天画像(3d)
            .bi_img (Array like (2d, uint8))        : BI画像(2d)
            .masked_bi_img (Array like (2d))        : カラス,太陽等のマスキングを行ったあとのbi画像
            .crow_area (float)                      : カラスが占める領域面積を保持
            .crow_is(bool)                          : カラスの有無があるかどうかを判定  Defaults to False
            .self.circle_area (int)                 : マスキングに使用するサークルのピクセル数
            .used_bi (bool)                         : ピクセル数が計算に使用できるかどうかを判定する.  Defaults to True.
            .used_area (int)                        : 計算に使用できるピクセル数
            .used_area_img (Array like (2d))        : 使用できるピクセルの二値画像
            .used_area_rate (float)                 : 使用できるピクセルの割合
            .masking_flag (bool)                    : マスキングを実行するかどうか Default to True.
        """
        super().__init__()  # スレッドクラスをオーバーライド
        self.wsi_path               = wsi_path      # 全天画像のパスを保持
        self.circle_dict            = circle_dict   # サークル画像のディクショナリ
        self.wsi_3d                 = None          # 使用する全天画像(RGB画像)
        self.bi_img                 = None          # BI画像(2d)
        self.masked_bi_img          = None          # マスキングを行ったあとのBI画像
        self.circle_bi_dict  = {}            # サークルでマスキングを行ったあとのBI画像
        self.used_bi                = True          # BIの計算に使用できるかどうかを判定する
        self.masking_flag           = masking       # minmaxでマスキングを実行するかどうか
        self.threshold_area         = threshold_area

    def run(self):
        """実行用メソッド
        """

        # 上限と下限を指定してbiを計算
        self.get_wsi_img(self.wsi_path)  # WSI画像を取得
        self.calc_bi_img()  # bi画像を作成

        if self.masking_flag:  # マスキングする場合
            self.bi_masking_minmax(min=15, max=250)  # BIをマスキング

        else:  #マスキングしない場合
            self.bi_no_masking()
        
        self.masking_circle(area=self.threshold_area)

    def get_wsi_img(self, path):
        """指定パスの全天画像をメモリに取り込む
        Args:
            path (str): 全天画像のパス(全天画像はjpg or png or tif)
        """
        self.wsi_3d = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
    
    def bi_masking_minmax(self, min=15, max=250):
        """指定強度のピクセルを用いて画像を再構成

        Args:
            min (int, optional): _description_. Defaults to 15.
            max (int, optional): _description_. Defaults to 250.
            area (float, optional): _description_. Defaults to 0.95.
        """
        self.masked_bi_img = np.where(
            (self.bi_img>min)&(self.bi_img<max),
            self.bi_img,
            np.nan
        )
    
    def bi_no_masking(self):
        """minmaxでマスキングを行わない
        """
        self.masked_bi_img = self.bi_img

    def calc_bi_img(self):
        """取り込んでいるWSIイメージからBI画像を算出

        Returns:
            Array like(2d, uint8); BIイメージ画像
        """
        self.bi_img = np.nansum(self.wsi_3d/3, axis=2).astype(np.uint8)
        return self.bi_img
    
    def masking_circle(self, area=0.95):
        """サークルでマスキングを行う. 使用可能かどうか判定も行う

        Args:
            circle_img  (Array like (2d))   : サークル画像
            circle_area (int)               : サークル画像の面積
        """
        for key, [circle_img, circle_area] in self.circle_dict.items():
            circle_masked_bi_img = np.where(circle_img==1, self.masked_bi_img, np.nan)
            available_rate = np.nansum(~np.isnan(circle_masked_bi_img)) / circle_area
            self.circle_bi_dict[key] = [
                circle_masked_bi_img,
                available_rate>area
            ]


# %%
#マルチスレッド処理(10分間隔5枚ずつ)
class MultiWsiImage:
    def __init__(
        self,
        input_dir_path = 'E:/ResearchData4/Level1/wsi_202209/',
        circle_dir = 'E:/ResearchData4/Level1/circle_img/',
        circle_ls = [75],
        masking_flag = True):
        """WSI画像の10分平均処理
        BI10分平均値を計算する。マルチスレッド対応済み

        Args:
            input_dir_path (str, path)              : 元画像の保存先ディレクトリ.
            masking_dir (str, path)                 : マスキング用サークル画像のディレクトリ
            circle_ls (list)                        : マスキング用サークルの開口角
            masking (bool)                          : カラス等のマスキングを実行するかどうか Default to True.

        Attributes:
            .input_dir_path (str, path)             : 元画像の保存先ディレクトリ
            .circle_dict (dict, (Array like, 2d))   : マスク用画像の配列をまとめた辞書
            .out_df (pandas.DataFrame)              : 出力用DataFrame
            .masking_flag (bool)                    : マスキングを実行するかどうか Default to True.
        """
        
        self.input_dir_path = input_dir_path
        self.circle_dict    = get_circle_img(circle_dir, circle_ls)
        self.out_df         = pd.DataFrame()  # 統計量記録用データフレーム
        self.masking_flag   = masking_flag
    
    def run(self, start, end, min_sun_height=5, min_used=1, lon=139.48, lat = 35.68, threshold_area=0.95):
        """複数時刻用(メイン関数)

        Args:
            start (datetime.datetime): 計算開始時刻
            end (datetime.datetime): 計算終了時刻
            min_sun_height (int, degree)        : 最低太陽高度. Defaults to 5.
            min_used (int, optional)            : 10分平均を算出する際に必要な画像の枚数. Defaults to 1.
            lon (float, optional)               : 全天カメラの設置場所の緯度. Defaults to 139.48.
            lat (float, optional)               : 全天カメラの設置場所の経度. Defaults to 35.68.
            threshold_area (float, optional)    : 統計量を算出するのに必要なピクセル割合. Defaults to 0.95.
        """
        threshold_sinh = np.sin(np.deg2rad(min_sun_height))
        date_loop_ls = np.arange(start, end, datetime.timedelta(minutes=10))
        for basedate_64 in date_loop_ls:
            basedate = pd.to_datetime(basedate_64)

            # 経過観察用
            if (basedate.hour==0)&(basedate.minute==0):
                print(f'Processing...{basedate.strftime("%Y/%m/%d")} (now:{datetime.datetime.now()})')

            now_sinh = calc_sinh(lon=lon, lat=lat, date=basedate)
            if now_sinh<threshold_sinh:  # 太陽高度が低すぎれば無視
                continue
            self.make_10min_img(basedate=basedate, threshold_area=threshold_area, min_used=min_used)

    
    def set_df(self, df, basedate, circle_key, used_img_dict, masked_img_dict, min_used):
        df.loc[basedate, f'BI_usedimg_{circle_key}'] = int(used_img_dict[circle_key])
        if used_img_dict[circle_key] < min_used:
            del masked_img_dict[circle_key]
            df.loc[basedate,f'BI_mean_{circle_key}'] = np.nan
            df.loc[basedate,f'BI_std_{circle_key}']  = np.nan
            df.loc[basedate,f'BI_max_{circle_key}']  = np.nan
            df.loc[basedate,f'BI_min_{circle_key}']  = np.nan
        else:
            convert_img = np.array(masked_img_dict[circle_key])
            del masked_img_dict[circle_key]
            df.loc[basedate,f'BI_mean_{circle_key}'] = np.nanmean(convert_img)
            df.loc[basedate,f'BI_std_{circle_key}']  = np.nanstd(convert_img)
            df.loc[basedate,f'BI_max_{circle_key}']  = np.nanmax(convert_img)
            df.loc[basedate,f'BI_min_{circle_key}']  = np.nanmin(convert_img)
        return df


    def make_10min_img(self, basedate, threshold_area=0.95, min_used=1):
        """10分平均画像作成用関数

        Args:
            basedate (datetime.datetime)    : 10分平均画像の基準時刻. この時刻の前5枚分を使用する
            threshold_area (float)          : 統計量を算出するのに必要なピクセル割合. Defaults to 0.95.
            min_used (int)                  : 10分平均を算出する際に必要な画像の枚数. Defaults to 1.
        """

        threads = []
        # スレッドを立てる(RGB画像を取得)
        for i in range(5):
            date = basedate - datetime.timedelta(minutes=i*2)
            date_str = datetime.datetime.strftime(date, '%Y%m%d_%H%M')
            img_path_ls = glob.glob(f'{self.input_dir_path}/{date_str}*.jpg')
            
            if len(img_path_ls)==0:
                continue  # 画像が見つからないときはスルー
            
            pwi = ProcessWsiImage(
                wsi_path=img_path_ls[0],
                masking=self.masking_flag,
                circle_dict=self.circle_dict,
                threshold_area=threshold_area
                )
            pwi.start()
            threads.append(pwi)
        
        # 開口度ごとに5枚の画像を保持するための辞書を作成
        masked_img_dict = {}
        used_img_dict = {}  # 使用した画像の枚数
        for circle_key in self.circle_dict.keys():
            masked_img_dict[circle_key] = []
            used_img_dict[circle_key] = 0

        # 各スレッドで作成したBI画像を辞書にまとめる
        for thread in threads:
            thread.join()
            # 
            for circle_key, [circle_img, img_judge] in thread.circle_bi_dict.items():
                self.used_img_num=0
                masked_img_ls = []
                if img_judge:
                    masked_img_dict[circle_key].append(circle_img)  # 使用可能なら足す
                    used_img_dict[circle_key]+=1
        
        set_df_threads = []
        # 各開口度ごとに統計量を算出
        for circle_key in self.circle_dict.keys():

            set_df_thread = threading.Thread(
                target=self.set_df,
                args=(self.out_df, basedate, circle_key, used_img_dict, masked_img_dict, min_used)
            )
            set_df_thread.start()
            set_df_threads.append(set_df_thread)
        for set_df_thread in set_df_threads:
            set_df_thread.join()

# %%
def split_sort_df(in_df, circle_ls, save_header):
    usedimg_df = pd.DataFrame()
    mean_df = pd.DataFrame()
    std_df = pd.DataFrame()
    max_df = pd.DataFrame()
    min_df = pd.DataFrame()
    for circle_angle in circle_ls:
        usedimg_df[circle_angle] = in_df[f'BI_usedimg_{circle_angle}']
        mean_df[circle_angle] = in_df[f'BI_mean_{circle_angle}']
        std_df[circle_angle] = in_df[f'BI_std_{circle_angle}']
        max_df[circle_angle] = in_df[f'BI_max_{circle_angle}']
        min_df[circle_angle] = in_df[f'BI_min_{circle_angle}']

        usedimg_df.to_csv(f'{save_header}_usedimg.csv')
        mean_df.to_csv(f'{save_header}_mean.csv')
        std_df.to_csv(f'{save_header}_std.csv')
        max_df.to_csv(f'{save_header}_max.csv')
        min_df.to_csv(f'{save_header}_min.csv')
    return usedimg_df, mean_df, std_df, max_df, min_df

# %% 処理部分
if __name__=='__main__':
    start = datetime.datetime.now()

    circle_ls = [50, 55, 60, 65, 70, 75, 80, 85, 90]  # 開口角のリスト
    #circle_ls = [85]


    mwi = MultiWsiImage(
        input_dir_path=f'T:/Uda/wsi_202209/',
        circle_dir='T:/Uda/circle_img/',
        circle_ls=circle_ls,
        masking_flag=False)
    masked_img_dict = mwi.run(
        start = datetime.datetime(2022, 8, 1, 0, 0, 0),
        end = datetime.datetime(2022, 9, 1, 0, 0, 1)
        )

    end = datetime.datetime.now()
    print(f'time :{(end - start).total_seconds()}s')

    split_sort_df(mwi.out_df, circle_ls , '../../python_test/wsi_test')  # 結果の出力


# %%
