"""
データセット（Pascal VOC） を、学習用に整備するスクリプト
・Usage
    python3  
"""

import argparse
import glob
import os

parser = argparse.ArgumentParser()
parser.add_argument('org_data_dir', type=str,
                    help='Path to the directory containing the PASCAL VOC data.')
parser.add_argument('--data_dir', type=str, default='./',
                    help='Path to the directory containing the PASCAL VOC data.')
parser.add_argument('--recursive', '-r',  action='store_true', 
                    help='data_dir から、再帰的にデータを探します.')
parser.add_argument('--output_path', type=str, default='.',
                    help='Path to the directory to create TFRecords outputs.')
parser.add_argument('--train_data_list', type=str, default='./train.txt',
                    help='Path to the file listing the training data.')
parser.add_argument('--valid_data_list', type=str, default='./val.txt',
                    help='Path to the file listing the validation data.')
parser.add_argument('--image_data_dir', type=str, default='./img',
                    help='The directory containing the image data.')
parser.add_argument('--label_data_dir', type=str, default='./annotimg',
                    help='The directory containing the augmented label data.')


if __name__ == '__main__':
    args = parser.parse_args()

    # Pascal VOC データを、datsaet/ 以下にコピーする。（まずは強制で）
    if args.recursive:
        xml_list = glob.glob(os.path.join(args.org_data_dir, '**', '*.xml'), recursive=True)
        img_list = glob.glob(os.path.join(args.org_data_dir, '**', '*.jpg'), recursive=True)
        img_list += glob.glob(os.path.join(args.org_data_dir, '**', '*.png'), recursive=True)
    else:
        xml_list = glob.glob(os.path.join(args.org_data_dir, '*.xml'))
        img_list = glob.glob(os.path.join(args.org_data_dir, '*.jpg'))
        img_list += glob.glob(os.path.join(args.org_data_dir, '*.png'))

    print(xml_list)    
    print(img_list)

