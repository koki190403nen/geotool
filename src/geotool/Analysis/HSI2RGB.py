#!/usr/bin/env python-3
# -*- coding: utf-8 -*-
# HSI画像をRGB空間に変換する

import numpy as np

def HSI2RGB(img):
    H,S,I = [img[:,:,i] for i in range(3)]
    I = I/255
    H_dash = H/60
    Z = 1 - np.abs((H_dash//2)-1)
    C = (3*I*S)/(1+Z)
    X = C*Z

    R_1 = np.where(
        np.isnan(H), 0, np.where(
        (0<=H_dash)&(H_dash<1), C, np.where(
        (1<=H_dash)&(H_dash<2), X, np.where(
        (2<=H_dash)&(H_dash<3), 0, np.where(
        (3<=H_dash)&(H_dash<4), 0, np.where(
        (4<=H_dash)&(H_dash<5), X, np.where(
        (5<=H_dash)&(H_dash<6), C, np.nan
        )))))))
    
    G_1 = np.where(
    np.isnan(H), 0, np.where(
    (0<=H_dash)&(H_dash<1), X, np.where(
    (1<=H_dash)&(H_dash<2), C, np.where(
    (2<=H_dash)&(H_dash<3), C, np.where(
    (3<=H_dash)&(H_dash<4), X, np.where(
    (4<=H_dash)&(H_dash<5), 0, np.where(
    (5<=H_dash)&(H_dash<6), 0, np.nan
    )))))))

    B_1 = np.where(
    np.isnan(H), 0, np.where(
    (0<=H_dash)&(H_dash<1), 0, np.where(
    (1<=H_dash)&(H_dash<2), 0, np.where(
    (2<=H_dash)&(H_dash<3), X, np.where(
    (3<=H_dash)&(H_dash<4), C, np.where(
    (4<=H_dash)&(H_dash<5), C, np.where(
    (5<=H_dash)&(H_dash<6), X, np.nan
    )))))))
    
    m=I*(1-S)
    R,G,B = R_1+m, G_1+m, B_1+m
    return np.array([R,G,B]).transpose([1,2,0])