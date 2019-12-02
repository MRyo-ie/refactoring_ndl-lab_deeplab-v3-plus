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
### [準備] モデル（転移学習用）
1. `./models/org_resnet/` ディレクトリを作る。
    ```
    $ mkdir -p  ./models/org_resnet/
    ```
2. （tensorflowの[slim](https://github.com/tensorflow/models/tree/master/research/slim)から）[resnet_v2_50_2017_04_14.tar.gz](http://download.tensorflow.org/models/resnet_v2_50_2017_04_14.tar.gz) を、1. にダウンロードする。
    ```
    $ cd  models/org_resnet/
    $ wget http://download.tensorflow.org/models/resnet_v2_50_2017_04_14.tar.gz  ./models/org_resnet/
    ```
3. 解凍
    ```
    $ tar -zxvf  resnet_v2_50_2017_04_14.tar.gz
    ```

### [準備] データセット
#### デモデータ（解体新書）
- すぐに train を実行できる。
    ```
    $ python3 train.py  ./data_in/datas_test/
    ```

#### 他の or 自作の データの場合
1. pascal VOC形式の xml フォーマットで、アノテーションを付与する。

### データの移動
- 作業の流れ
  - `data_in/datas/【dataset名】/` 以下に、`img`、`xml` ディレクトリを作って、そこにデータを入れる。
  - `$ cd data_in` して、
    - `draw_annot_img.py  datas/【dataset名】/`
    - `create_pascal_tf_record.py  datas/【dataset名】/`
  
    を実行する。

- 手動で行っても良いが、自動で行うスクリプトを作ったので、それを使っても良い。
  1. データのパスを確認する。
      - .zip や .tar.gz の場合は、先に解凍しておく。
      - 相対バスを指定する場合は、この README.md がある位置を基準とする。
  2. `data_in/datas/【dataset名】/xml`に、画像を`data_in/datas/【dataset名】/img`に入れる。
      ```
      $ python3 init_dataset.py  【dataset名】  【1. のパス】
      ```
      - `【dataset名】` は自分で決める。
      - オプションで以下を追加できる。
        - `-m`
          - `data_in/datas/【dataset名】` ディレクトリがすでに存在する場合、削除しない（データをマージする）
        - `-r`
          - `【1. のパス】` 以下を、再帰的に探索する。

  3. アノテーション画像を生成する。
      ```
      $ cd data_in
      $ python3 draw_annot_img.py  datas/【dataset名】
      ```
      - セグメンテーション画像ファイルが `data_in/datas/【dataset名】/annot_img` に生成される。
  4. TFRecode を生成する。
      ```
      $ python3 create_pascal_tf_record.py  datas/【dataset名】
      ```




### Training
- デモ版（「解体新書」2クラス）を実行する場合
    ```bash
    $ python3 train.py
    ```
- 自分のデータセットを実行する場合
    ```bash
    $ python3 train.py  data_in/datas/【dataset名】
    ```

## 技術的な話
- `create_pascal_tf_record.py` で TFRecode を作成している。
- 



# original リポジトリ情報
- [ndl-lab](https://github.com/ndl-lab)
  - [tensorflow-deeplab-v3-plus](https://github.com/ndl-lab/tensorflow-deeplab-v3-plus)
  - [NDLDocLデータセット](https://github.com/ndl-lab/layout-dataset)

