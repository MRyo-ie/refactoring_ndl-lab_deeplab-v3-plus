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
from multiprocessing import Process
import numpy as np
import pandas as pd
import time
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




# ラベル設定 を読み込み
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
            shutil.copytree(setting_dir_path, './_settings')
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

    # 「ラベル設定」 を読み込み
    label_order_list = load_label_setting(setting_dir_path)
    print('[Info] 【ラベル設定】', end='')
    print(*label_order_list, sep='\n    ')

    print('\n[Info] アノテーション画像の生成を開始します。')
    # 全annotationファイルのパス（list）を取得
    anntfs = glob.glob(os.path.join('annt', "*."+annotate_ext))
    random.shuffle(anntfs)
    os.makedirs('annt_img', exist_ok=True)

    epoch = -1
    # time_make_dict = 0
    # time_make_annt_img = 0
    # time_write_img = 0
    p_list = []
    train_files = []
    val_files = []
    for anntf in tqdm(anntfs[:epoch]):
        # xml に対応する画像を探す。（画像の拡張子に対応するため。本当は png に統一したいけど...）
        img_fname = os.path.basename(anntf[:-3]) + "*"
        img_fpath = glob.glob(os.path.join('img', img_fname))[0]
        imgf = os.path.basename(img_fpath)
        # multiprocessing で並列処理する。
        p = Process(target=annotate_process, args=[anntf, imgf, label_order_list])
        p.start()
        p_list.append(p)
        ### 学習用とテスト用に分割
        if random.random() < 0.1:
            val_files.append(imgf + '\n')
        else:
            train_files.append(imgf + '\n')
    for p in tqdm(p_list):
        p.join()

    with open('train.txt', 'w') as ft:
            ft.writelines(train_files)
    with open('val.txt', 'w') as fv:
            fv.writelines(val_files)

    # print('[Info] time_make_dict     : ', time_make_dict)
    # print('[Info] time_make_annt_img : ', time_make_annt_img)
    # print('[Info] time_write_img     : ', time_write_img)
    """
    100% 100/100 [00:03<00:00, 27.02it/s]
    [Info] time_make_dict     :  0.010479927062988281
    [Info] time_make_annt_img :  0.1326291561126709
    [Info] time_write_img     :  2.363025426864624

    100% 100/100 [00:03<00:00, 30.10it/s]
    [Info] time_make_dict     :  0.019048690795898438
    [Info] time_make_annt_img :  0.0998697280883789
    [Info] time_write_img     :  1.9962170124053955
    """


def annotate_process(anntf, imgf, label_order_list):
    try:
        tree = ET.parse(anntf)
    except ET.ParseError as ex:
        print(ex, '\n    [Debug] anntf : ', anntf)
    root = tree.getroot()

    # 「xyタプルの辞書」を作る
    xy_dict = {}
    for object_tree in root.findall('object'):
        class_name = object_tree.find('name').text
        # （ラベル設定）同じラベルとして見る ものは、label_order_list の最初の要素(idx==0)に統一する。
        for row in label_order_list:
            if class_name in row:
                class_name = row[0]
        if class_name not in xy_dict:
            xy_dict[class_name] = []
        
        bndbox = object_tree.find("bndbox")
        # xy = ((xmin, ymin), (xmax, ymax))
        xy = (
            ( int(bndbox.find("xmin").text), int(bndbox.find("xmax").text) ),
            ( int(bndbox.find("ymin").text), int(bndbox.find("ymax").text) )
        )
        xy_dict[class_name].append(xy)

    # 「ラベル設定リスト」と「xyタプルの辞書」 を元に、教師画像を作成。
    size_tree = root.find('size')
    width = int(size_tree.find('width').text)
    height = int(size_tree.find('height').text)
    annotate_img = np.zeros((height, width, 1), np.uint8)
    for cls_idx in range(1, len(label_order_list)):
        # （ラベル設定）同じラベルとして見る ものは、label_order_list の最初の要素(idx==0)に統一する。
        cls_name = label_order_list[cls_idx][0]
        if cls_name in xy_dict:
            xys = xy_dict[cls_name]
            try:
                for x, y in xys:
                    # NumPyインデックススライス + 代入
                    annotate_img[y[0]:y[1], x[0]:x[1]] = cls_idx   * 25  # 画像として見たいなら、コメントを外す。
                    # print(annotate_img[y[0]:y[1], x[0]:x[1]])
            except:
                print('\n---------------\n[Error] アノテーション画像の生成に失敗しました。')
                print('''   file name : {}
                    class_name : {}
                    width, height  :  {}, {}
                    ((xmin, xmax), (ymin, ymax))  :  {}
                    '''.format(anntf, class_name, width, height, xy))

    cv2.imwrite(os.path.join("annt_img", imgf), annotate_img)




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
