#/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bin2Cont.py: バイナリの時系列配列を、1が何回連続したかに変換するクラス
# %%
import numpy as np

class Bin2Cont:

    def __init__(self, in_arr=None):
        """バイナリ時系列の連続具合を数値化する

        Attributes:
            in_arr  : 入力時系列バイナリ ([0,1,1,1,0,0,...])
            serial  : 1の塊ごとに番号をふった配列 ([0,1,2,3,0,0,...])
            inv_arr : 逆方向に番号を振った配列 ([0,3,2,1,0,0,...])

        Args:
            in_arr (Array Like): バイナリ形式の時系列配列
        """
        self.in_arr =in_arr

    def __call__(self, in_arr=None):
        if (self.in_arr is not None) & (in_arr is None):
            pass
        else:
            self.in_arr = in_arr
        self.calc_serial().calc_length().calc_inverse()
        return self.serial

    def calc_serial(self):
        """元の時系列を0,1,2,0,0,1,0のように変換する
        """
        out_ls = []
        for i, val in enumerate(self.in_arr):
            if i==0:
                out_ls.append(val)
                continue

            out_ls.append((out_ls[i-1]+1)*val)
        self.serial = np.array(out_ls)
        return self
    
    def calc_length(self):
        out_ls = []
        for i, (in_val, ser_val) in enumerate(zip(self.in_arr[::-1], self.serial[::-1])):
            if i==0:
                out_ls.append(ser_val)
                continue
            if out_ls[i-1]>ser_val:
                out_ls.append(out_ls[i-1]*in_val)
            elif ser_val>0:
                out_ls.append(ser_val)
            else:
                out_ls.append(0)
                
        self.len_arr = np.array(out_ls[::-1])
        return self
    
    def calc_inverse(self):
        self.inv_arr = np.where(self.serial>0, self.len_arr-self.serial+1, 0)
        return self
    
def osero(arr):
    """_summary_

    Args:
        arr (_type_): _description_

    Returns:
        _type_: _description_
    """

    out_ls = []

    for i, val in enumerate(arr):
        if (i==0)|(i==(len(arr)-1)):
            out_ls.append(val)
            continue
        if (arr[i-1]==1)&(arr[i+1]==1):
            out_ls.append(1)
            continue
        out_ls.append(val)
    return np.array(out_ls)
# %%
b2c = Bin2Cont()
b2c([0,0,0,1,1,1,1,0,0,1,1])