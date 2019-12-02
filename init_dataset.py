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
DATA_HOME_DIR = os.path.join(os.getcwd(), 'data_in')
os.chdir(DATA_HOME_DIR)
from data_in import draw_annot_img


parser = argparse.ArgumentParser()
parser.add_argument('org_data_dir', type=str,
                    help='Path to the directory containing the Orignal PASCAL VOC data.')
parser.add_argument('data_dir', type=str,
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

    # Pascal VOC データを、data_in/ 以下にコピーする。（まずは強制で）
    print('=====  {}  ====='.format(args.data_dir))
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
    
    ###  data_in/【data_dir】 に annot_img などのディレクトリを作成  ###
    # data_dir がすでにある場合は、削除する。（-m でマージ：削除しない）
    if os.path.exists(args.data_dir) and not args.merge:
        shutil.rmtree(args.data_dir)
        print('[Info] データディレクトリを削除しました！')
    # ディレクトリ作成
    os.makedirs(args.data_dir, exist_ok=True)
    os.chdir(args.data_dir)
    if not os.path.exists('annot_img'):
        os.mkdir('annot_img')
        os.mkdir('xml')
        os.mkdir('img')
    
    ###  data_in/ 以下にコピー  ###
    print('[Info] xml のコピーを開始します')
    for p in tqdm(xml_list):
        cp_fpath = os.path.join('xml', os.path.basename(p))
        if os.path.exists(cp_fpath):
            # すでにコピー済みのファイルは飛ばす。
            continue
        shutil.copy(os.path.join(org_data_dir, p), cp_fpath)
    
    print('[Info] img のコピーを開始します')
    for img_fpath in tqdm(img_list):
        cp_fpath = os.path.join('img', os.path.basename(p))
        if os.path.exists(cp_fpath):
            continue
        shutil.copy(os.path.join(org_data_dir,p), cp_fpath)
    
    # -a を実行
    print('[Info] data_in/ へのコピーが完了しました。')
    if args.all_process:
        os.chdir(DATA_HOME_DIR)
        draw_annot_img.draw(args.data_dir)
        os.chdir(DATA_HOME_DIR)
        subprocess.run(['python3','create_pascal_tf_record.py', args.data_dir])
        print('[Info] 全ての工程が完了しました！\n    すぐに train.py を実行できます。')
    else:
        print('[Info] README.md を参考に、次の工程に進んでください。')


