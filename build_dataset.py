"""
## 処理内容
1. copy_dataset.py を実行
    - data_in/datas/【データセット名】 以下に、データをコピー。
        - .xml or .json → annotate
        - .jpg and .png → img
2. draw_annot_img.py を実行
    - 正解画像（アノテーションした画像）を作成。
        - annotate_img
        - train.txt, val.txt

このスクリプトを実行後、以下を実行して、データセット完成。
3. make_pascal_tf_record.py を実行
    - tf_record を作成。
        - voc_train.record, voc_val.record
"""
import os
from data_in import copy_dataset
from data_in import draw_annot_img
# from data_in import make_pascal_tf_record

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('org_data_dir', type=str,
                    help='Path to the directory containing the Orignal PASCAL VOC data.')
parser.add_argument('data_dir', type=str,
                    help='Path to the directory containing the Copy PASCAL VOC data.')
parser.add_argument('--annotate_ext', '-ant_ext', default='xml', 
                    help='アノテーションファイルの拡張子を指定します。（xml, json）')
parser.add_argument('--recursive', '-r',  action='store_true', 
                    help='data_dir から、再帰的にデータを探します.')
parser.add_argument('--skip_copy', '-not_cp',  action='store_true', 
                    help='copy 処理をスキップします。')
parser.add_argument('--init_data_dir', '-init',  action='store_true', 
                    help='すでに data_dir が存在する場合、削除します。 default： True')
parser.add_argument('--setting_dir_path', '-set_path', default='', 
                    help='ラベル設定（_settings/）がすでにあるなら、そこからコピーします。')



if __name__ == "__main__":
    args = parser.parse_args()

    os.chdir('data_in')
    print(os.getcwd())

    ### 絶対パスに変換
    # args.data_dir
    DATA_HOME_DIR = os.getcwd()
    data_dir = os.path.join(DATA_HOME_DIR, args.data_dir)
    # args.setting_dir_path
    setting_dir_path = args.setting_dir_path
    if args.setting_dir_path != '':
        setting_dir_path = os.path.abspath(args.setting_dir_path)

    ### 処理開始
    print('\n=====  {}  ====='.format(args.data_dir))
    print('[Info] copy_dataset')
    if not args.skip_copy or not os.path.exists(args.data_dir):
        copy_dataset.copy(
            args.org_data_dir,
            data_dir,
            args.annotate_ext,
            args.recursive,
            args.init_data_dir)
    else:
        print('[Info] コピー処理はスキップされました。')

    print('[Info] draw_annot_img')
    print('[Info] setting_dir_path : {}'.format(setting_dir_path))
    draw_annot_img.draw(data_dir, args.annotate_ext, setting_dir_path)
    print('\n')

