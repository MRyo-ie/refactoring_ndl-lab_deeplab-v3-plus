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

# カレントディレクトリ（想定：このスクリプトがある場所。data_in/）
DATA_HOME_DIR = os.getcwd()
from data_in import draw_annot_img


parser = argparse.ArgumentParser()
parser.add_argument('org_data_dir', type=str,
                    help='Path to the directory containing the Orignal PASCAL VOC data.')
parser.add_argument('data_dir', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')
parser.add_argument('--annotate_ext', '-ant_ext',  default='xml', 
                    help='data_dir から、再帰的にデータを探します.')
parser.add_argument('--recursive', '-r',  action='store_true', 
                    help='data_dir から、再帰的にデータを探します.')
parser.add_argument('--init_data_dir', '-init',  action='store_true', 
                    help='すでに data_dir が存在する場合、削除します。 default： True')
# parser.add_argument('--all_process', '-a',  action='store_true', 
#                     help='makeannotimage.py、create_pascal_tf_record.py まで、まとめて実行します。')




def copy(org_data_dir, data_dir, annotate_ext, recursive, init_data_dir):
    # Pascal VOC データを、data_in/ 以下にコピーする。（まずは強制で）
    ###  データ一覧を取得  ###
    os.chdir(org_data_dir)
    xml_list = glob.glob('**/*.' + annotate_ext, recursive=recursive)
    img_list = glob.glob('**/*.'+'jpg', recursive=recursive)
    img_list += glob.glob('**/*.'+'png', recursive=recursive)

    if len(xml_list) == 0:
        print('annotate_ext : ' + annotate_ext)
        print(xml_list)
        print(img_list)
        print('[Error] Pascal VOC データが見つかりませんでした。')
        sys.exit(1)
    
    ###  data_in/【data_dir】 に annot_img などのディレクトリを作成  ###
    # data_dir がすでにある場合は、削除する。（-m でマージ：削除しない）
    if os.path.exists(data_dir) and init_data_dir:
        shutil.rmtree(data_dir)
        print('[Info] データディレクトリを削除しました！')
    # ディレクトリ作成
    os.makedirs(data_dir, exist_ok=True)
    os.chdir(data_dir)
    print('[Info] cd data_dir　→ ' + os.getcwd())
    if not os.path.exists('annt_img'):
        os.makedirs('annt_img', exist_ok=True)
        os.makedirs('annt', exist_ok=True)
        os.makedirs('img', exist_ok=True)
    
    ###  data_in/ 以下にコピー  ###
    print('[Info] {} のコピーを開始します'.format(annotate_ext))
    for p in tqdm(xml_list):
        cp_fpath = os.path.join('annt', os.path.basename(p))
        if os.path.exists(cp_fpath):
            # すでにコピー済みのファイルは飛ばす。
            continue
        shutil.copy(os.path.join(org_data_dir, p), cp_fpath)
    
    print('[Info] img のコピーを開始します')
    for p in tqdm(img_list):
        cp_fpath = os.path.join('img', os.path.basename(p))
        if os.path.exists(cp_fpath):
            continue
        shutil.copy(os.path.join(org_data_dir, p), cp_fpath)
    
    # # -a を実行
    # print('[Info] data_in/ へのコピーが完了しました。')
    # if all_process:
    #     os.chdir(DATA_HOME_DIR)
    #     draw_annot_img.draw(data_dir)
    #     os.chdir(DATA_HOME_DIR)
    #     subprocess.run(['python3','create_pascal_tf_record.py', data_dir])
    #     print('[Info] 全ての工程が完了しました！\n    すぐに train.py を実行できます。')
    # else:
    #     print('[Info] README.md を参考に、次の工程に進んでください。')

# example on how to use it
if __name__ == "__main__":
    args = parser.parse_args()

    # 絶対パスに変換
    data_dir = os.path.join(DATA_HOME_DIR, args.data_dir)

    print('=====  {}  ====='.format(args.data_dir))
    copy(
        args.org_data_dir,
        data_dir,
        args.annotate_ext,
        args.recursive,
        args.init_data_dir )

