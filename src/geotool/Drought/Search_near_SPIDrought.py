import numpy as np
from ..Analysis import Bin2Cont

class Search_near_SPIDrought:
    def __init__(self):
        pass
    

    def shift_2d(self, arr, start, end):
        """探索範囲を0軸に持つ時系列データを生成

        Args:
            arr (_type_): _description_
            start (_type_): 探索範囲の開始ポイント
            end (_type_): 探索範囲の終了ポイント

        Returns:
            _type_: _description_
        """
        out_2d = np.zeros((end-start+1, len(arr)))
        for i, shiftsize in enumerate(range(start, end+1)):
            out_2d[i, :] = np.roll(arr, shift=shiftsize*-1)
            if shiftsize>0:
                out_2d[i, shiftsize*-1:]=0
            else:
                out_2d[i,:shiftsize*-1]=0
        return out_2d
    
    def osero(self, vci_drought):
        """前後が干ばつで、真ん中が違う点を干ばつに置き換える"""
        out_ls = []

        for i, val in enumerate(vci_drought):
            if (i==0)|(i==(len(vci_drought)-1)):
                out_ls.append(val)
                continue
            if (vci_drought[i-1]==1)&(vci_drought[i+1]==1):
                out_ls.append(1)
                continue
            out_ls.append(val)
        return np.array(out_ls)


    def fit(self, vci_drought, spi_drought, start, end, vci_size=2, osero=False):
        """指定した農業干ばつの発生時期周辺で気象干ばつが発生しているかどうかを判断する

        Args:
            vci_drought (Array like): 農業干ばつの発生の有無
            spi_drought (Array like): 気象干ばつの発生の有無
            start (int): 探索の開始ポイント
            end (int): 探索の終了ポイント
            vci_size (int, optional): 農業干ばつの最小期間長. Defaults to 2.
        """
        if osero:
            vci_drought = self.osero(vci_drought)
        b2c_vci = Bin2Cont().fit(vci_drought)
        shifted_ts = self.shift_2d(spi_drought, start, end)

        term = vci_drought.astype(bool)&(b2c_vci.serial==1)&(b2c_vci.len_arr>=vci_size)

        self.include_spi_drought = shifted_ts[:,term].any(axis=0)
        self.term = term

        return shifted_ts[:,term].any(axis=0)
