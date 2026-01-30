#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2つの配列のうち、片方だけ動かす


def MoveFunction(moved_input, fixed_input, lag=0, cutsize=23):
    # lagが正ならmoved_inputを後ろに動かす

    # 前後をカット
    if cutsize is not None:
        moved_input = moved_input[cutsize:-1*cutsize]
        fixed_input = fixed_input[cutsize:-1*cutsize]
    

    if lag>0:  # lagが正の時
        moved_arr = moved_input[: -1*lag]  # 動かす方は後ろを削る
        fixed_arr = fixed_input[lag:]  # 固定側は前を削る
    elif lag==0:
        moved_arr = moved_input
        fixed_arr = fixed_input
    elif lag<0:  # lagが負の時
        moved_arr = moved_input[-1*lag :]  # 動かす方は前を削る
        fixed_arr = fixed_input[: lag]  # 固定側は後ろを削る
    
    return moved_arr, fixed_arr