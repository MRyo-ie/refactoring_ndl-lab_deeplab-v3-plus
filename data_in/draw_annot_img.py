# -*- coding: utf-8 -*-
import argparse
import csv
import glob
import os
import random
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

"""
README.md 参照。
"""

random.seed(777)

parser = argparse.ArgumentParser()
parser.add_argument('data_dir', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')
parser.add_argument('--annotate_ext', '-ant_ext', default='xml', 
                    help='アノテーションファイルの拡張子を指定します。（xml, json）')
parser.add_argument('--setting_dir_path', '-set_path', default='', 
                    help='ラベル設定（_settings/）がすでにあるなら、そこからコピーします。')


# xyリスト の 辞書を作る
# （ここでやる）

# 「クラス：番号」辞書と「xyリスト」 の辞書 を元に、教師画像を作成。


# ラベルの順番を指定する csv ファイル（空）を作る
def load_label_setting(setting_dir_path=''):
    """
    【実装内容】
        ● 初回（作業ディレクトリに、_settings/ がない場合）
            ・_settings/ が他の場所にあるなら、setting_dir_path で指定する。
                ・ コピーして、先に進む。
            ・まず、_settings/ ディレクトリを作る。
                _settings/
                    |- all.txt
                    |- set_order.txt
                    |- set_cluster.json
                    |- _tmp.json (自動生成)
            ・順番を指定するようにメッセージを表示して、sys.exit() する。
        ● ２回目（作業ディレクトリに、jsonがある場合）
            1. json を読み込み（全ラベル:_all、指定ラベル:_order）
            2. 同じラベルとして扱うものを指定するリストも作る。
    ● json ファイルの編集の仕方
        ・ 重なったときに下になるラベルから順に並べる。
            ※ 含めないラベルは除外する。
        ・ 同じラベルとしてまとめる場合
            ・ 〜.json に、まとめるラベルをリストとして並べる。
    return:
        除外、順番 が加味された ラベルリスト。
        要素のインデックス が、正解ラベル番号に対応する。
        例） 「1_overall：一番下の層」「9_table：一番上の層」「5_stanp は除外」 の例。
            [[], [1_overall], [4_illustration], [2_handwritten, 3_typography], 
             [8_textline], [6_headline, 7_caption], [9_table]]
        将来的には、これがベクトルになる？
    """
    if not os.path.exists('_settings'):
        if setting_dir_path != '':
            if os.path.basename(setting_dir_path) != '_settings':
                raise IllegalLabelSettingException('_settings/ のパスが不正です。', setting_dir_path)
            shutil.copytree(setting_dir_path, './')
        else:
            ##  初回  ##
            print('[Info] _settings ファイルが見つかりませんでした。新規作成します。')
            os.mkdir('_settings')
            Path("_settings/all.txt").touch()
            Path("_settings/set_order.csv").touch()
            print('[Info] _settings/ 以下のテキストファイルを、README.md に沿って埋めてください。')
            sys.exit(0)
    else:
        # すでにある場合は、そちらが優先される。
        pass
    ##  2回目  ##
    # 設定ファイルを読み込む。 →　list 化する。
    with open('_settings/all.txt', 'r') as all_f:
        l_all = all_f.readlines()
        if len(l_all) < 1:
            raise IllegalLabelSettingException('_settings/all.txt が空です。  label all : ', l_all)
    with open('_settings/set_order.csv', 'r') as order_f:
        reader = csv.reader(order_f) # readerオブジェクトの作成
        label_order_list = [r for r in reader if len(r) > 0]
        if len(label_order_list) < 1:
            raise IllegalLabelSettingException('_settings/set_order.txt が空です。')
    
    label_order_list.insert(0, [])  # インデックスを対応させる（背景として扱う）ために、0番目は埋める
    return label_order_list
    
class IllegalLabelSettingException(Exception):
    """ラベル設定ファイルに不備があった場合に投げられる例外"""
    pass



def draw(data_dir, annotate_ext, setting_dir_path):
    os.chdir(data_dir)

    # ラベル設定 を読み込み
    label_order_list = load_label_setting(setting_dir_path)
    print(label_order_list)

    # 全annotationファイルの パス（list）を取得
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
        try:
            tree = ET.parse(filename)
        except ET.ParseError as ex:
            print(ex, '\n    [Debug] filename : ', filename)
        root = tree.getroot()
        size_tree = root.find('size')
        width = int(size_tree.find('width').text)
        height = int(size_tree.find('height').text)
        annotate_img = np.zeros((height, width, 1), np.uint8)

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
                            annotate_img[y, x] = max(1, annotate_img[y, x])
                elif class_name != "1_overall":
                    for y in range(xy['ymin'], xy['ymax']):
                        for x in range(xy['xmin'], xy['xmax']):
                            annotate_img[y, x] = 3
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
        cv2.imwrite(os.path.join("annt_img", imgfilename), annotate_img)
    ft.close()
    fv.close()


def labeling(class_name, xy, annotate_img):
    for y in range(xy['ymin'], xy['ymax']):
        for x in range(xy['xmin'], xy['xmax']):
            annotate_img[y, x] = max(1, annotate_img[y, x])



# example on how to use it
if __name__ == "__main__":
    args = parser.parse_args()
    # img, annt, annt_img のあるディレクトリに cd する。
    DATA_HOME_DIR = os.getcwd()
    data_dir = os.path.join(DATA_HOME_DIR, args.data_dir)

    setting_dir_path = args.setting_dir_path
    if args.setting_dir_path != '':
        setting_dir_path = os.path.abspath(args.setting_dir_path)
    print('{}'.format(setting_dir_path))

    draw(data_dir, args.annotate_ext, setting_dir_path)
