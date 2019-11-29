import cv2
import glob
import numpy as np
import os
import pandas as pd
import random
from tqdm import tqdm
from xml.etree import ElementTree as ET

"""
preprocess/ に cd してから実行しないと、エラーになる。
"""

random.seed(777)

class XML_preprocessor(object):

    def __init__(self):
        self.xml_dir = 'annotxml'
        self.num_classes = 3
        self.data = dict()
        self._preprocess_XML()

    def _preprocess_XML(self):
        filenames = glob.glob(os.path.join(self.xml_dir, "*.xml"))
        random.shuffle(filenames)
        ft = open('train.txt', 'w')
        fv = open('val.txt', 'w')
        for filename in tqdm(filenames):
            # xml に対応する画像を探す。（画像の拡張子に対応するため。本当は png に統一したいけど...）
            img_filepath = glob.glob(os.path.join('img', os.path.basename(filename[:-3]) + "*"))[0]
            imgfilename = os.path.basename(img_filepath)
            tree = ET.parse(filename)
            root = tree.getroot()
            flag = False
            size_tree = root.find('size')
            width = int(size_tree.find('width').text)
            height = int(size_tree.find('height').text)
            annotimg = np.zeros((height, width, 1), np.uint8)
            for object_tree in root.findall('object'):
                flag = True
                class_name = object_tree.find('name').text
                xmin = int(object_tree.find("bndbox").find("xmin").text)
                ymin = int(object_tree.find("bndbox").find("ymin").text)
                xmax = int(object_tree.find("bndbox").find("xmax").text)
                ymax = int(object_tree.find("bndbox").find("ymax").text)
                if class_name == "4_illustration":
                    for y in range(ymin, ymax):
                        for x in range(xmin, xmax):
                            # 1_overall よりは下（隠れる）
                            annotimg[y, x] = max(150, annotimg[y, x])
                elif class_name != "1_overall":
                    for y in range(ymin, ymax):
                        for x in range(xmin, xmax):
                            annotimg[y, x] = 200
                else:
                    o_xmin, o_xmax, o_ymin, o_ymax = xmin, xmax, ymin, ymax
            if random.random() < 0.1:
                fv.write(imgfilename + "\n")
            else:
                ft.write(imgfilename + "\n")
            cv2.imwrite(os.path.join("annotimg", imgfilename), annotimg)
        ft.close()
        fv.close()


if __name__ == "__main__":
    # example on how to use it
    import pickle
    XML_preprocessor()
