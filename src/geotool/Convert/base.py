#!/usr/bin/env python3
# -*- cording: utf-8 -*-
# データ変換クラスの基底クラス

# %%
import numpy as np
from matplotlib import pyplot as plt
import glob

# 自作ツール
from .arr2tif import arr2tif

# %%
class Convert:
    def __init__(self):
        self.img = None  # メイン部分(ndarray形式)
        self.h = None  # メイン部分の高さ
        self.w = None  # メイン部分の幅
        self.dtype = None  # メイン部分のdtype
        self.in_extension ='.nc'  # 入力データの拡張子
        self.out_extension = '.tif'  # 出力データの拡張子
        self.arr_extension = '.raw'  # ndarrayの拡張子(自己定義)
        
        self.geotrans = None  # 地理情報

##### 書き直すもの#############################################################
    # [入力] -> self.arr その他複数情報を抜き出す
    def in2arr(self, in_file_path):
        self.img = None
        self.h, self.w, self.dtype = None, None, None
        self.geotrans = None
        pass

    # self.arr -> [out]
    def arr2out(self, out_file_path):
        pass

    # 出力画像の名前を決める(拡張子以外の部分)
    def make_out_file_name(self, in_file_name):
        return in_file_name.split('.')[0] + f'.h{self.h}w{self.w}_{self.dtype}'  # 拡張子を省いてヘッダーをつけて出力

    # 地理情報を作成する
    def make_geotrans(self):
        pass

##### 実際に使う関数(そのまま触らない) ######################################################
    # [入力]をndarrayに変換して保存(1枚だけ)
    def save_arr_single(self, in_file_path, out_file_path):
        self.in2arr(in_file_path)
        self.img.tofile(out_file_path)
        print(out_file_path)
    
    # [入力]をndarrayに変換して保存(ディレクトリ内)
    def save_arr_multi(self, in_dir_path, out_dir_path):
        get_file_ls = glob.glob(in_dir_path+'/*'+self.in_extension)
        for get_file_name in get_file_ls:
            in_file_name = get_file_name.split('\\')[-1]
            in_file_path = in_dir_path + '/' + in_file_name

            self.in2arr(in_file_path)  # self.imgを入手
            out_file_name = self.make_out_file_name(in_file_name)+self.arr_extension  # 出力画像のファイル名
            out_file_path = f'{out_dir_path}/{out_file_name}'
            self.img.tofile(out_file_path)  # ndarrayを保存
            print(out_file_path)  # DEBUG

    # [入力]を[出力]に変換して保存(1枚だけ)
    def save_out_single(self, in_file_path, out_file_path):
        self.in2arr(in_file_path)  # [入力]をself.imgに変換する
        self.arr2out(out_file_path)  # self.imgを[出力]に変換する

    # [入力]を[出力]に変換して保存(ディレクトリ内)
    def save_out_multi(self, in_dir_path, out_dir_path):
        get_file_ls = glob.glob(f'{in_dir_path}/*{self.in_extension}')
        for get_file_path in get_file_ls:
            in_file_name = get_file_path.split('\\')[-1]
            in_file_path = in_dir_path + '/' + in_file_name  # 入力画像のファイルパス
            self.in2arr(in_file_path)  # [入力] -> self.imgに変換

            out_file_name = self.make_out_file_name(in_file_name)+self.out_extension  # 出力画像のファイル名
            out_file_path = f'{out_dir_path}/{out_file_name}'  # 出力画像のファイルパス
            self.arr2out(out_file_path)  # 出力

