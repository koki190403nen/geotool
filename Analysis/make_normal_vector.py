#!/usr/bin/env python-3
# -*- coding:utf-8 -*-
# make_normal_vector.py: 任意の点からMultistringsへの法線を作成する
import numpy as np
from shapely import LineString
import shapely

# 最も近いセグメントと投影点を見つける
def make_normal_vector(multiline, point, one_sided_width):

    # 最も近いセグメントと投影点を見つける
    min_dist = float('inf')
    closest_proj = None
    closest_seg = None

    for line in multiline.geoms:
        coords = list(line.coords)
        for i in range(len(coords) - 1):
            a = np.array(coords[i][:2])
            b = np.array(coords[i + 1][:2])
            ab = b - a
            ap = np.array(point.coords[0]) - a
            t = np.clip(np.dot(ap, ab) / np.dot(ab, ab), 0, 1)
            proj = a + t * ab
            dist = np.linalg.norm(np.array(point.coords[0]) - proj)
            if dist < min_dist:
                min_dist = dist
                closest_proj = proj
                closest_seg = (a, b)

    # 法線ベクトルの計算（セグメントに垂直な単位ベクトル）
    seg_vec = closest_seg[1] - closest_seg[0]
    normal_vec = np.array([-seg_vec[1], seg_vec[0]])  # 垂直方向
    unit_normal = normal_vec / np.linalg.norm(normal_vec)

    # 法線ラインの作成（30mずつ両方向に延ばす）
    start = closest_proj - one_sided_width * unit_normal
    end = closest_proj + one_sided_width * unit_normal
    normal_line = LineString([start, end])
    return normal_line