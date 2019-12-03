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
parser.add_argument('data_dir_name', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')


def draw(data_dir_name):
    # img, annotxml, annotimg のあるディレクトリに cd する。
    os.chdir(data_dir_name)

    filenames = glob.glob(os.path.join('xml', "*.xml"))
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
            xmin = int(object_tree.find("bndbox").find("xmin").text)
            ymin = int(object_tree.find("bndbox").find("ymin").text)
            xmax = int(object_tree.find("bndbox").find("xmax").text)
            ymax = int(object_tree.find("bndbox").find("ymax").text)
            try:
                if class_name == "4_illustration":
                    for y in range(ymin, ymax):
                        for x in range(xmin, xmax):
                            # 1_overall よりは下（隠れる）
                            annotimg[y, x] = max(1, annotimg[y, x])
                elif class_name != "1_overall":
                    for y in range(ymin, ymax):
                        for x in range(xmin, xmax):
                            annotimg[y, x] = 2
                # else:
                #     o_xmin, o_xmax, o_ymin, o_ymax = xmin, xmax, ymin, ymax
            except:
                print('\n---------------\n[Error] アノテーション画像の生成に失敗しました。')
                print('''   file name : {}
                    class_name : {}
                    width, height  :  {}, {}
                    xmin, xmax, ymin, ymax  :  {}, {}, {}, {}
                    '''.format(filename, class_name, width, height, xmin, xmax, ymin, ymax))
        if random.random() < 0.1:
            fv.write(imgfilename + "\n")
        else:
            ft.write(imgfilename + "\n")
        cv2.imwrite(os.path.join("annot_img", imgfilename), annotimg)
    ft.close()
    fv.close()


# example on how to use it
if __name__ == "__main__":
    args = parser.parse_args()
    draw(args.data_dir_name)
