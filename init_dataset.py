# -*- coding: utf-8 -*-
"""
データセット（Pascal VOC） の
    ・ダウンロード
    ・data_in/user_datas/【データセット名】/  にコピー
まで行う。
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('org_data_dir', type=str,
                    help='Path to the directory containing the Orignal PASCAL VOC data.')
parser.add_argument('data_dir_name', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')
parser.add_argument('--recursive', '-r',  action='store_true', 
                    help='data_dir から、再帰的にデータを探します.')
parser.add_argument('--merge', '-m',  action='store_true', 
                    help='すでに data_dir が存在する場合、削除せずマージします。 default： True')
parser.add_argument('--all_process', '-a',  action='store_true', 
                    help='makeannotimage.py、create_pascal_tf_record.py まで、まとめて実行します。')


def glob_datas(p_dir, ext, recursive=False):
    # パスから、正規表現に引っかかるものを削除
    os.chdir(p_dir)
    return glob.glob('**/*.{}'.format(ext), recursive=recursive)


if __name__ == '__main__':
    args = parser.parse_args()
    cd = os.getcwd()

    # Pascal VOC データを、datsaet/ 以下にコピーする。（まずは強制で）
    print('=====  {}  ====='.format(args.data_dir_name))
    ###  データ一覧を取得  ###
    org_data_dir = os.path.abspath(args.org_data_dir)
    print('recursive  : ', args.recursive)
    xml_list = glob_datas(org_data_dir, 'xml', recursive=args.recursive)
    img_list = glob_datas(org_data_dir, 'jpg', recursive=args.recursive)
    img_list += glob_datas(org_data_dir, 'png', recursive=args.recursive)

    if len(xml_list) == 0:
        print(xml_list)
        print(img_list)
        print('[Error] Pascal VOC データが見つかりませんでした。')
        sys.exit(1)
    
    ###  data_in/【データ名】 に annot_img などのディレクトリを作成  ###
    # python スクリプトのある場所に移動
    user_datas_path = os.path.join(cd, 'data_in', 'user_datas')
    if not os.path.exists(user_datas_path):
        os.makedirs(user_datas_path)
    os.chdir(user_datas_path)
    # data_dir がすでにある場合は、削除する。（-m でマージ：削除しない）
    if os.path.exists(args.data_dir_name) and not args.merge:
        shutil.rmtree(args.data_dir_name)
        print('[Info] データディレクトリを削除しました！')
    # ディレクトリ作成
    os.makedirs(args.data_dir_name, exist_ok=True)
    os.chdir(args.data_dir_name)
    if not os.path.exists('annot_img'):
        os.mkdir('annot_img')
        os.mkdir('xml')
        os.mkdir('img')
    
    ###  data_in/ 以下にコピー  ###
    print('[Info] xml のコピーを開始します')
    for xml_fpath in tqdm(xml_list):
        shutil.copy(os.path.join(org_data_dir,xml_fpath), 'xml/')
    print('[Info] img のコピーを開始します')
    for img_fpath in tqdm(img_list):
        shutil.copy(os.path.join(org_data_dir,img_fpath), 'img/')
    
    print('[Info] data_in/ へのコピーが完了しました。')
    print('[Info] README.md を参考に、次の工程に進んでください。')

