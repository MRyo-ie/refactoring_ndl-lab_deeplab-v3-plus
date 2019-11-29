# 図表抽出(Image extraction)

このプログラムは以下のリポジトリ(MITライセンス)を改変して作成しています。

[rishizek's repo](https://github.com/rishizek/tensorflow-deeplab-v3-plus).

## Setup
TensorFlow (r1.6)以降と Python 3をお使いください。

## Predict
1. model50ディレクトリを作る。
2. [学習済重みファイル](http://lab.ndl.go.jp/dataset/trainedweights.zip)をダウンロード、解凍して、1. に配置する。
3. 以下を実行。
    ```bash
    python3 picture_extraction.py --input_dir INPUT_DIR --output_dir OUTPUT_DIR
    ```

## Train
### データセット を準備
1. pascal VOC形式の xml フォーマットで、
    - 図表領域 ： "4_illustration"
    - 資料全体 ： "1_overall"

   のアノテーションを付与してください。

2. 作成したxmlを`preprocess/annotxml`に、画像をpreprocess/imgに入れる。
3. アノテーション結果画像を生成する。
    ```
    $ cd preprocess
    $ python makeannotimage.py
    ```
    で、セグメンテーション画像ファイルが`preprocess/annotimg`に生成される。


### モデル（転移学習用） を準備
1. `ini_checkpoints/resnet_v2_50` ディレクトリを作る。
2. tensorflowの[slim](https://github.com/tensorflow/models/tree/master/research/slim)から[resnet_v2_50_2017_04_14.tar.gz](http://download.tensorflow.org/models/resnet_v2_50_2017_04_14.tar.gz) をダウンロードして、1. に配置する。


### Training
```bash
$ python3 create_pascal_tf_record.py
$ python3 train_3class_50.py
```
を実行すると学習が始まります。

## 技術的な話
- `create_pascal_tf_record.py` で TFRecode を作成している。
- 



# original リポジトリ情報
- [ndl-lab](https://github.com/ndl-lab)
  - [tensorflow-deeplab-v3-plus](https://github.com/ndl-lab/tensorflow-deeplab-v3-plus)
  - [NDLDocLデータセット](https://github.com/ndl-lab/layout-dataset)

