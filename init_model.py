"""
データセット（Pascal VOC） を、学習用に整備するスクリプト
・Usage
    python3  
"""

import argparse
import glob
import os
import shutil
import sys
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('learn_data_dir', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')
parser.add_argument('--org_data_dir', type=str, default=None,
                    help='Path to the directory containing the Orignal PASCAL VOC data.')
parser.add_argument('--recursive', '-r',  action='store_true', 
                    help='data_dir から、再帰的にデータを探します.')
parser.add_argument('--init',  action='store_true', 
                    help='data_dir を初期化（全データ削除）します。default：False')


def glob_datas(p_dir, ext, recursive=False):
    return glob.glob(os.path.join(
                    os.path.abspath(args.org_data_dir), '**', '*.'+ext),
                    recursive=True  )


if __name__ == '__main__':
    args = parser.parse_args()

    if len(xml_list) == 0:
        print('[Error] Pascal VOC データが見つかりませんでした。')
        sys.exit(1)
    
    if not os.path.exists()
    # python スクリプトのある場所に移動
    org_data_dir = os.path.abspath(args.org_data_dir)
    os.chdir('./dataset')

    if not os.path.exists(args.learn_data_dir):
        os.makedirs(args.learn_data_dir)
    
    os.chdir(args.learn_data_dir)
    if not os.path.exists('annotimg'):
        os.mkdir('annotimg')
        os.mkdir('annotxml')
        os.mkdir('img')
    
    # Pascal VOC データを、datsaet/ 以下にコピーする。（まずは強制で）
    xml_list = glob_datas(args.org_data_dir, 'xml', recursive=args.recursive)
    img_list = glob_datas(args.org_data_dir, 'jpg', recursive=args.recursive)
    img_list += glob_datas(args.org_data_dir, 'png', recursive=args.recursive)

    for xml_fpath in tqdm(xml_list):
        shutil.copyfile(xml_fpath, './')
    for img_fpath in tqdm(img_list):
        shutil.copyfile(img_fpath, './')
    
    print('dataset/ へのコピーが完了しました。')
    print('README.md を元に、次の工程に進んでください。')

