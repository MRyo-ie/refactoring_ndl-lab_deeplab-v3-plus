# 表層メタ情報を deeplab v3+（Semantic Segmentaiton） で読み取る。

このプログラムは以下のリポジトリ(MITライセンス)を改変して作成しています。

[rishizek's repo](https://github.com/rishizek/tensorflow-deeplab-v3-plus).

## Setup
- 推奨環境
  - Python3
  - TensorFlow (r1.6)以降
- pip
  ```
  $ pip3 install -r requirements.txt
  ```

## Predict
1. model50ディレクトリを作る。
2. [学習済重みファイル](http://lab.ndl.go.jp/dataset/trainedweights.zip)をダウンロード、解凍して、1. に配置する。
3. 以下を実行。
    ```bash
    python3 picture_extraction.py --input_dir INPUT_DIR --output_dir OUTPUT_DIR
    ```

## Train
### データセット を準備
#### 自作データ の場合
1. pascal VOC形式の xml フォーマットで、アノテーションを付与する。

### データの移動
1. ダウンロード／既存 のデータのパスを確認する。
2. `data_in/【dataset名】/xml`に、画像を`data_in/【dataset名】/img`に入れる。
    ```
    $ python3 init_dataset.py  【dataset名】  【1. のパス】
    ```
    - オプションで以下を追加できる。
      - `-m`
        - `data_in/【dataset名】` ディレクトリがすでに存在する場合、削除しない（データをマージする）
      - `-r`
        - `【1. のパス】` 以下を、再帰的に探索する。

3. アノテーション画像を生成する。
    ```
    $ cd data_in
    $ python draw_annot_img.py  【dataset名】
    ```
    で、セグメンテーション画像ファイルが`data_in/annot_img`に生成される。
4. tensorflow で扱い易いように、TFRecode に変換する。
    ```
    $ python create_pascal_tf_record.py  【dataset名】
    ```



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

