#!/usr/bin/env python3
# -*- cording:utf-8 -*-
# 区分線形回帰を行う(bfast)

# %%
import numpy as np
from scipy.optimize import curve_fit, least_squares
from matplotlib import pyplot as plt
import warnings

warnings.simplefilter('ignore')

# %%
class PiecewiseRegression:
    def __init__(self, inflection_pred=True):
        self.x = None  # オリジナルの曲線のxの値
        self.y = None  # オリジナルの曲線のyの値
        self.n = None  # 折れ線の数
        self.inflection_pred = inflection_pred  # 変曲点数の予測を行うかどうか
        self.xi = []  # 得られた変曲点のx座標
        self.yi = []  # 得られた変曲点のy座標
        self.ki = []  # 得られた折れ線の傾き
        self.bi = []  # 得られた折れ線の切片
        self.b0 = None  # 最初の直線の切片
        self.p = None  # 得られたパラメータ
        self.e = None  # 得られた推定共分散
        self.bic_ls = []  # 予測中のBICをすべて計算
        self.bic = None  # BICの推定量を保存
        self.pred = None  # 推定値を保存
        self.thisfunc = None  # 推定に使った関数を保管
        self.line_count = None  # 推定された折れ線の数

    def fit(self, x, y, n=None, stepwise='forward'):
        self.x = x  # オリジナルのxの値を与える
        self.y = y  # オリジナルのyの値を与える


        # BICが最小になるまで繰り返す

        # 勾配のくぼみ探す
        if stepwise=='forward':
            for i in range(int(len(x) / 2)):
                self.fit_piecewise(n=i+1)
                bic_now = self.calc_bic()  # BICを推定

                if i!=0:
                    if bic_now > bic_before:
                        break
                bic_before = bic_now
            self.line_count = i
            self.bic = bic_before
        
        # 総当たり方式
        elif stepwise=='backward':
            bic_ls = []
            for i in range(int(len(x) / 10)):
                self.fit_piecewise(n=i+1)
                bic_now = self.calc_bic()  # BICを推定
                bic_ls.append(bic_now)
            
            bic_best_idx = np.argmin(np.array(bic_ls))  # ベストなbicの時のノードの数
            self.line_count = bic_best_idx + 1
            self.bic = bic_ls[bic_best_idx]
        
        self.fit_piecewise(n=self.line_count)
        self.calc_section()  # 切片の計算


    
    # paramの数から変曲点の数を割り出し、折れ線モデルを定義
    def piecewise(self, x, *params):
        # paramsは(b0, k0 /x1, k1 /x2, k2 /...)
        line_cnt = int(len(params)/2)
        ki_ls = list(params)[1::2]  # 傾きをまとめたリスト
        b0 = list(params)[0]  # 切片の初期値
        xi_ls = [-np.inf] + list(params)[0::2][1:] + [np.inf]  # 変曲点のx座標をまとめたリスト
        if line_cnt==1:
            return b0 + ki_ls[0] * x  # 線分が一つならシンプルな線形回帰
        
        out = float(0)
        x00 = float(0)
        for i in range(line_cnt):
            x0, xi, ki = xi_ls[i], xi_ls[i+1], ki_ls[i]
            if i ==0:
                k0 = ki
                yi = b0
                out += ((x0<x)&(x<=xi)) * (ki*x + b0)
            else:
                yi += k0*(x0-x00)  # yiを更新

                out += ((x0<x)&(x<=xi)) * (yi + (x-x0)*ki)
            k0 = ki  # 次のyiの更新の為に現在のkiをki-1として保存
            x00 = x0 if i>=1 else 0  # 次のyiの更新の為にx_i-2を保存
            
        return out

    # 1回だけpiecewiseをfittingさせる
    def fit_piecewise(self, n, x=None, y=None):
        # nは折れ線の数
        if x is not None:
            self.x, self.y = x, y
        
        self.p, self.e = curve_fit(self.piecewise, self.x, self.y, p0=np.ones(n*2))
        self.pred = self.piecewise(self.x, self.p)

        self.thisfunc = self.piecewise
        self.save_params()
        return self.p

    # パラメータを分けて保管
    def save_params(self):
        self.b0 = self.p[0]  # 切片の初期値
        self.ki = self.p[1::2]  # 傾きのパラメータ
        self.thisfunc = self.piecewise  # 関数を保管
        if len(self.p)>=3:
            self.xi = np.array(self.p[0::2][1:])  # 変曲点のx座標
        else:
            self.xi = np.nan

    # bicを算出する
    def calc_bic(self):
        # BIC = n * ln(RSS/n) + K * ln(n)
        # n: データ数
        # RSS: 残差二乗和
        # K: モデルに含まれるパラメータ数
        self.pred = self.predict(self.x)
        n = len(self.x)
        RSS = np.nansum((self.y - self.pred)**2)
        K = len(self.p)

        BIC = n * np.log(RSS/n) + K*np.log(n)
        return BIC

    # fitting後に与えられたxについて所持しているパラメータをもとにyを予測
    def predict(self, x):
        return self.thisfunc(x, *self.p)

    # 各線の切片と、各変曲点のy座標を計算する
    def calc_section(self):
        b = self.b0  # 最初の切片を登録

        if self.line_count==1:
            return
        self.bi.append(self.b0)

        # 各線ごとに切片と変曲点のy座標を計算
        for i, xi in enumerate(self.xi):
            yi = self.piecewise(xi, *self.p)  # 変曲点のy座標
            self.yi.append(yi)
            b = yi - xi*self.ki[i+1]
            self.bi.append(b)  # リストに切片を登録


    # summaryを表示
    def summary(self):
        print(f'BIC  {self.bic}')
        print(f'line: {self.line_count}')
        print(f'Turning xi: {self.xi}')
        print(f'Turning yi: {self.yi}')
        print(f'ki: {self.ki}')
        print(f'bi: {self.bi}')


# %%
if __name__=='__main__':
    pr = PiecewiseRegression(True)

    # サンプルデータの作成
    x = np.arange(0, 300)
    y = pr.piecewise(x, 0, 0.5, 100, 5)
    y_noise = y + np.random.randn(len(y)) * 10
    plt.scatter(x, y_noise, s=8)


    pr.fit(x, y_noise, estimate=0)
    y_pred = pr.predict(x)
    plt.plot(x, y_pred, c='red')
    plt.scatter(pr.xi, pr.yi, c='red', s = 25)

    pr.summary()
# %%