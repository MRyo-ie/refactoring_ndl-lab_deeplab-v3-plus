# 表層メタ情報を deeplab v3+（Semantic Segmentaiton） で読み取る。

このプログラムは以下のリポジトリ(MITライセンス)を改変して作成しています。

[rishizek's repo](https://github.com/rishizek/tensorflow-deeplab-v3-plus).

# Setup
- 推奨環境
  - Python3
  - TensorFlow (r1.6)以降
- pip
  ```
  $ pip3 install -r requirements.txt
  ```

# Predict
1. model50ディレクトリを作る。
2. [学習済重みファイル](http://lab.ndl.go.jp/dataset/trainedweights.zip)をダウンロード、解凍して、1. に配置する。
3. 以下を実行。
    ```bash
    python3 picture_extraction.py --input_dir INPUT_DIR --output_dir OUTPUT_DIR
    ```

# Train
## 【準備】 モデル（転移学習用）
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

## 【準備】 データセット

### デモデータ（「解体新書」） を試す場合
- アノテーション画像（教師画像）を生成。
    ```
    $ cd data_in
    $ python3 draw_annot_img.py  datas_test
    ```
- アノテーション画像（教師画像）を生成。
    ```
    $ python3 create_pascal_tf_record.py  datas_test
    ```

### 他の or 自作の データの場合
- pascal VOC形式の xml フォーマットで、アノテーションを付与する。
- データを、作業ディレクトリにコピー
  - `data_in/datas/【dataset名】/` 以下に「`img`」「`xml`」 ディレクトリを作って、そこにデータを入れる。
    - `data_in/datas_demo/` が参考になるはず。
  - 手動で行っても良いが、自動で行うスクリプトを作ったので、それを使っても良い。
    1. 元データのパスを確認する。
        - .zip や .tar.gz の場合は、先に解凍しておく。
        - 相対バスを指定する場合は、この README.md がある位置を基準とする。
    2. スクリプトを使って、作業ディレクトリにコピーする。
        ```
        $ cd data_in
        $ python3 copy_dataset.py  【1. のパス】  datas/【dataset名】 
        ```
        - `【dataset名】` は自分で決める。
        - オプションで以下を追加できる。
          - `-m`
            - `data_in/datas/【dataset名】` ディレクトリがすでに存在する場合、コピーをスキップする。（削除しない）
          - `-r`
            - `【1. のパス】` 以下を、再帰的に探索する。
          - ~~`-a`~~
            - ~~データ生成の全ての工程を、一気に（同時に）実行する。~~
            - ~~これをつけた場合は、以下の「教師データ生成」は実行しなくてOK~~
            - ~~エラーが出た場合は、↓以下の２つを再度実行すれば OK~~
- 教師データ生成
  1. アノテーション画像を生成する。
      ```
      $ cd data_in
      $ python3 draw_annot_img.py  datas/【dataset名】 -set_path 【_settings/ のパス】
      ```
      - セグメンテーション画像ファイルが `data_in/datas/【dataset名】/annot_img` に生成される。
      - `-set_path`
        - 「使用するラベル」「ラベルの順番」を指定するための `_settings/` がすでにあるなら、そのパスを指定する。（作業ディレクトリにコピーされる）
        - 初めての場合は、このオプションは使わない。
          - 未指定の場合は、`_settings/` が新規作成される。
          - 新規作成されたら、そこで一旦スクリプトが終了するので、設定ファイルを編集する。
          - 以下のようにして書き込む。
            - `all.txt`
              - 全てのラベル名を書き込む
              - 1ラベルごとに改行する。
              - 例） datas_demo
                ```
                1_overall
                2_handwritten
                3_typography
                4_illustration
                5_stamp
                6_headline
                7_caption
                8_textline
                9_table
                ```
            - `set_order.csv`
              - 「使用するラベル」「ラベルの順番」 を指定する。
              - 「使用するラベル」
                - 学習したいラベルだけを書く。
                - 書かなかったラベルは、アノテーション画像には追加されない。
              - 「ラベルの順番」
                - 重なった時に、どのラベルが上に来る（優先される）かを指定する。
                - １行目が一番**下**の層。
                - 最終行が一番**上**の層。
              - 例）datas_demo
                ```
                1_overall
                4_illustration
                2_handwritten,3_typography
                8_textline
                6_headline,7_caption
                9_table
                ```
                - `5_stamp` を除外し、2と3、6と8 を同じラベルとして扱う設定例。
                - この例のラベルの次元数は 6。
                - 2次元配列として読み込まれる。
  2. TFRecode を生成する。
      ```
      $ python3 create_pascal_tf_record.py  datas/【dataset名】
      ```

- `build_dataset.py` は、`copy_dataset.py` と `draw_annot_img.py` をまとめて実行するスクリプト。
  - `copy_dataset.py`　を手動で行う（`copy_dataset.py` が使えない）状況の場合は、これを使う必要はない。
  - `create_pascal_tf_record.py` は実行する必要がある。
  - 引数は、`copy_dataset.py` と `draw_annot_img.py` をまとめたもの。


## Training
- デモ版（「解体新書」2クラス）を実行する場合
    ```bash
    $ python3 train.py  \
            data_in/datas/datas_test \
            --batch_size=1
    ```
- 自分のデータセットを実行する場合
    ```bash
    $ python3 train.py  data_in/datas/【dataset名】
    ```


# original リポジトリ情報
- [ndl-lab](https://github.com/ndl-lab)
  - [tensorflow-deeplab-v3-plus](https://github.com/ndl-lab/tensorflow-deeplab-v3-plus)
  - [NDLDocLデータセット](https://github.com/ndl-lab/layout-dataset)

