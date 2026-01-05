# %%
import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal 
import geopandas as gpd
from PIL import Image
import tqdm
import os, glob, shutil
import pypdf

if __name__=='__main__':
    from geotrans2extent import geotrans2extent
else:
    from .geotrans2extent import geotrans2extent
import warnings;warnings.simplefilter('ignore')


# %%
class VisualInspectinMaterials:
    def __init__(self):
        """目視確認資料の作成 (3行x2列で構成)
        """
        self.fig, self.axes = None, None
        self.raster_img = None

        self.txt_params = {
            'axis_titles':{
                1: '国土地理院地形図',
                2: 'PlanetScope前画像(21/03/26)',
                3: 'PlanetScope後画像(24/03/07)',
                4: 'Googleアーカイブ前画像(21/03/31)',
                5: 'Googleアーカイブ後画像(24/02/11)'
            },
            'credits':{
                0: 'Includes material © 2024 Planet. \nAll rights reserved.',
                1: 'Copyright. Geospatial Information \nAuthority of Japan. ALL RIGHTS RESERVED.',
                2: 'Includes material © 2021 Planet. All rights reserved.',
                3: 'Includes material © 2024 Planet. All rights reserved.',
                4: '© Google',
                5: '© Google'
            },
            'in_dir_paths':{
                1: f'./02_DATA/Level3/目視判読用元画像/①国土地理院地図/',
                2: f'./02_DATA/Level3/目視判読用元画像/②PlanetScope前画像/',
                3: f'./02_DATA/Level3/目視判読用元画像/③PlanetScope後画像/',
                4: f'./02_DATA/Level3/目視判読用元画像/④Googleアーカイブ前画像',
                5: f'./02_DATA/Level3/目視判読用元画像/⑤Googleアーカイブ後画像'
            },
            'suptxts':{
                'address':'住所',
                'area':'area'
            },
            'add_suptxts':['LULC_code']
        }

    def out_1page(self, id, it):
        self.set_figure()
        self.plot_mapping(id)
        self.plot_png(id)
        self.set_axis_txts()
        self.set_suptxt(id, it)


    def fit(self, vector_path, raster_path, out_pdf_path=None, working_dir_path='./working/', id_title='id', png=False):
        if os.path.exists(working_dir_path):
            shutil.rmtree(working_dir_path)
        os.makedirs(working_dir_path, exist_ok=True)  # 一次ファイル出力先ディレクトリ
        
        self.set_mapping(vector_path=vector_path, raster_path=raster_path, id_title=id_title)
        

        pbar = tqdm.tqdm(total=len(self.point_gdf[id_title]))
        ext = 'png' if png is True else 'pdf'
        for it, id in enumerate(self.point_gdf[id_title]):
            self.out_1page(id, it)
            plt.savefig(f'{working_dir_path}/ID{id}.{ext}')
            plt.clf()
            plt.close()
            pbar.update(1)
            
        pbar.close()

        # 結合操作を書く
        merger = pypdf.PdfMerger()
        for id in self.point_gdf[id_title]:
            merger.append(F'{working_dir_path}/ID{id}.pdf')

        merger.write(out_pdf_path)
        merger.close()


    #### 複数枚を同時実行する関数を作成する

    def set_figure(self):
        """pdf1ページ分のfigureを作成する
        """
        if self.fig is not None:
            del self.fig, self.axes
        
        plt.rcParams['font.family'] = 'Meiryo'
        plt.rcParams['font.size'] = 8
        self.fig, self.axes = plt.subplots(3,2, figsize=(8.27, 11.69), dpi=150)
        plt.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.20, hspace=0.15, wspace=0.02)


    def set_mapping(self, vector_path, raster_path, id_title='id'):
        """axis[0,0]に図示する、位置を示す図のための情報の読み込み。読み込むGISデータの座標系はepsg=4326にしておく

        Args:
            vector_path (path, geojson etc.): ポイントを表示するためのgeojsonのパス
            raster_path (path, geotiff): 背景にするgeotiffのパス。3バンド(r,g,b)でマスク部分はnull,データは0~255にしておく。
            id_title (str): 読み込んだベクターデータのID列の列名。 Defaults to 'id'.

        """

        self.id_title = id_title
        self.point_gdf = gpd.read_file(vector_path).to_crs(epsg=4326)
        self.point_gdf[id_title] = self.point_gdf[id_title].astype(str)
        src = gdal.Open(raster_path)
        img = src.ReadAsArray().transpose((1,2,0))
        h,w = img.shape[0], img.shape[1]
        self.raster_img = np.where(np.isnan(img), 255, img).astype(np.uint8)
        
        self.raster_extent = geotrans2extent(src.GetGeoTransform(), h,w)
        del src


    def plot_mapping(self, id):
        """axes[0,0]にマップを表示する。指定したIDのポイントを強調する

        Args:
            id (int): 指定ID
        """
        self.point_gdf.plot(ax=self.axes[0,0], color='yellow', markersize=10)
        self.point_gdf.query(f'{self.id_title}=="{id}"').plot(ax=self.axes[0,0], color='blue', markersize=200, marker='*')
        self.axes[0,0].imshow(self.raster_img, extent=self.raster_extent)
        self.axes[0,0].grid(alpha=0.5)

        # フォントサイズの設定
        #self.axes[0,0].set_xticklabels(self.axes[0,0].get_xticklabels(), fontsize='x-small')
        #self.axes[0,0].set_yticklabels(self.axes[0,0].get_yticklabels(), fontsize='x-small')
    
    def plot_png(self, id):
        """self.txt_params['in_dir_paths']で指定したaxesにjpg/png画像を挿入する

        Args:
            id (int): 指定id
        """
        for i in range(1, 6):
            in_dir_path = self.txt_params['in_dir_paths'][i]
            path = glob.glob(f'{in_dir_path}/*_ID{id}*.png')[0]
            row, col = i//2, i%2
            img = Image.open(path)
            self.axes[row, col].imshow(img)
        
    
    def set_axis_txts(self):
        """axes中の脚注等を表示させる
        """
        for i in range(6):
            row, col = i//2, i%2
        
            if i!=0:
                self.axes[row, col].set_title(self.txt_params['axis_titles'][i], y=-0.10)
                self.axes[row, col].set_axis_off()
            self.axes[row, col].text(0.99, 0.02, self.txt_params['credits'][i], transform=self.axes[row, col].transAxes, ha='right', fontsize=5)

    def set_suptxt(self, id, it):
        self.fig.suptitle(f'抽出箇所の変化確認資料 {it+1}/{self.point_gdf.shape[0]}')

        geo_items = self.point_gdf.query(f'{self.id_title}=="{id}"')


        area_size = geo_items[self.txt_params["suptxts"]["area"]].values[0]
        area_size = format(int(area_size), ",") if type(area_size) is int else area_size

        detail_txts = f'ID：{id}'+\
            f'\n住所：{geo_items[self.txt_params["suptxts"]["address"]].values[0]}'+\
            f'\n座標：{geo_items.geometry.x.round(3).values[0]}°N, {geo_items.geometry.x.round(3).values[0]}°E'+\
            f'\n抽出面積：{area_size}$m^2$,'


        if 'add_suptxts' in self.txt_params.keys():
            for t in self.txt_params['add_suptxts']:
                detail_txts += f'\n{t}：{geo_items[t].values[0]}'

        self.fig.text(0.14, 0.955, detail_txts, ha='left', va='top')



