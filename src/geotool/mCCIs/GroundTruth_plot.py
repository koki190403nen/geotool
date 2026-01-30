# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import json
import datetime
# %%
def GroundTruth_plot(year, month, day, area='Fuchu', sample_dir = '../..//sample/'):


    with open(f'{sample_dir}/dataset/ccis_json/Fuchu.json', 'r') as f:
        dataset = json.load(f)

    mRR95wn = np.array(dataset['mRR95wn']['values'])
    mRR95wn_date = np.array([i for i in range(1, 366+1)])
    RR95wn = dataset['RR95wn']

    df = pd.read_csv(f'{sample_dir}/Amedas/Fuchu.csv', index_col=0)
    df.index = pd.to_datetime(df.index)
    ppt = df['PPT']
    date_arr = pd.to_datetime(df.index)

    start_date = pd.to_datetime(datetime.datetime(year, month, day))-datetime.timedelta(days=7)  # こいつを調整

    end_date = start_date + datetime.timedelta(days=15)

    weather_df = df.loc[(df.index>=start_date) & (df.index<=end_date)]

    using_ppt       = ppt[(date_arr>=start_date)&(date_arr<=end_date)]
    using_date      = date_arr[(date_arr>=start_date)&(date_arr<=end_date)]
    using_mRR95wn   = mRR95wn[(mRR95wn_date>=start_date.dayofyear) & ((mRR95wn_date<=end_date.dayofyear))]


    fig, ax = plt.subplots(figsize=(9, 4))
    plt.tight_layout(rect=(0.05, 0.12, 0.95, 0.95))
    ax.bar(using_date, using_ppt, width=0.5, label='Daily PPT')
    ax.hlines(RR95wn, using_date[0], using_date[-1], colors='green', label='Original Threshold')
    ax.plot(using_date, using_mRR95wn, c='red', label='modified Threshold')

    ax.grid()
    ax.set_xticks(using_date, using_date.strftime("%y/%m/%d"), rotation=-45)
    ax.set_xlabel('date', fontsize=12)
    ax.set_ylabel('PPT [mm]', fontsize=12)
    ax.legend()
    return fig, ax, weather_df

if __name__=='__main__':
    GroundTruth_plot(1993, 8, 13).show()

# %%
