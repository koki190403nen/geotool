#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# MakeProjectDirectory.py: 自分用のプロジェクトディレクトリを作成する

# %%
import os
def MakeProjectDirectory():
    os.makedirs(f'.//01_協議資料', exist_ok=True)
    os.makedirs(f'.//02_DATA', exist_ok=True)
    os.makedirs(f'.//03_codes', exist_ok=True)
    os.makedirs(f'.//04_QGIS', exist_ok=True)
    os.makedirs(f'.//05_解析結果', exist_ok=True)
    os.makedirs(f'.//99_その他', exist_ok=True)

    [os.makedirs(f'.//02_DATA//Level{i}', exist_ok=True) for i in range(4)]

    if os.path.isfile('../test.py'):
        with open(f'.//test.py', 'a') as f:
            pass
    if os.path.isfile('../test2.py'):
        with open(f'.//test2.py', 'a') as f:
            pass

