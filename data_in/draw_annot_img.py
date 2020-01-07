# -*- coding: utf-8 -*-
import argparse
import cv2
import glob
import numpy as np
import os
import pandas as pd
import random
from tqdm import tqdm
from xml.etree import ElementTree as ET

"""
README.md 参照。
"""

random.seed(777)

parser = argparse.ArgumentParser()
parser.add_argument('data_dir', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')
parser.add_argument('--annotate_ext', '-ant_ext', default='xml', 
                    help='アノテーションファイルの拡張子を指定します。（xml, json）')

# ラベルの順番を指定した json ファイルを作る
# 1. 重なったときに下になるラベルから順に並べる
#     ※ 含めないラベルは除外する。
# 2. 同じラベルとして扱うものを指定するリストも作る。

# ↑ を読み込むスクリプトを作る
# 1. json 読み込み
# 2. { クラス名： ラベル番号 } の辞書を作る。

# xyリスト の 辞書を作る
# （ここでやる）

# 「クラス：番号」辞書と「xyリスト」 の辞書 を元に、教師画像を作成。
label_order = []
label_dict = {
    '1_overall': 1, '2_handwritten': 4, '3_typography': 4, '4_illustration': 2,
    '5_stamp': 8, '6_headline': 6, '7_caption': 6, '8_textline': 5, '9_table': 9
}

def labeling(class_name, xy, annotimg):
    for y in range(xy['ymin'], xy['ymax']):
        for x in range(xy['xmin'], xy['xmax']):
            annotimg[y, x] = max(1, annotimg[y, x])


def draw(annotate_ext):
    filenames = glob.glob(os.path.join('annt', "*."+annotate_ext))
    random.shuffle(filenames)
    ft = open('train.txt', 'w')
    fv = open('val.txt', 'w')

    print('\n[Info] アノテーション画像の生成を開始します。')
    for filename in tqdm(filenames):
        # xml に対応する画像を探す。（画像の拡張子に対応するため。本当は png に統一したいけど...）
        img_fname = os.path.basename(filename[:-3]) + "*"
        img_fpath = glob.glob(os.path.join('img', img_fname))[0]
        imgfilename = os.path.basename(img_fpath)

        tree = ET.parse(filename)
        root = tree.getroot()
        size_tree = root.find('size')
        width = int(size_tree.find('width').text)
        height = int(size_tree.find('height').text)
        annotimg = np.zeros((height, width, 1), np.uint8)

        for object_tree in root.findall('object'):
            class_name = object_tree.find('name').text
            xy = {
                'xmin' : int(object_tree.find("bndbox").find("xmin").text),
                'ymin' : int(object_tree.find("bndbox").find("ymin").text),
                'xmax' : int(object_tree.find("bndbox").find("xmax").text),
                'ymax' : int(object_tree.find("bndbox").find("ymax").text),
            }
            try:
                # 1_overall|2_handwritten|3_typography|4_illustration|5_stamp|6_headline|7_caption|8_textline|9_table
                # 3クラス版（）
                if class_name == "4_illustration":
                    for y in range(xy['ymin'], xy['ymax']):
                        for x in range(xy['xmin'], xy['xmax']):
                            # 一番下（隠れる）
                            annotimg[y, x] = max(1, annotimg[y, x])
                elif class_name != "1_overall":
                    for y in range(xy['ymin'], xy['ymax']):
                        for x in range(xy['xmin'], xy['xmax']):
                            annotimg[y, x] = 3
                # 全クラス版

            except:
                print('\n---------------\n[Error] アノテーション画像の生成に失敗しました。')
                print('''   file name : {}
                    class_name : {}
                    width, height  :  {}, {}
                    xmin, xmax, ymin, ymax  :  {}, {}, {}, {}
                    '''.format(filename, class_name, width, height, xy['xmin'], xy['xmax'], xy['ymin'], xy['ymax']))
        if random.random() < 0.1:
            fv.write(imgfilename + "\n")
        else:
            ft.write(imgfilename + "\n")
        cv2.imwrite(os.path.join("annt_img", imgfilename), annotimg)
    ft.close()
    fv.close()



# example on how to use it
if __name__ == "__main__":
    args = parser.parse_args()
    # img, annotxml, annotimg のあるディレクトリに cd する。
    os.chdir(args.data_dir)
    draw(args.annotate_ext)
