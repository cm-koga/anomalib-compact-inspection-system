# anomalib-compact-inspection-system
Anomalibで生成した異常モデルをつかった簡易外観検査ソフト

Lightweight visual inspection software using an Anomalib-based anomaly detection model.

# Setup
* Python 3.11 or later

```bash
git clone https://github.com/cm-koga/anomalib-compact-inspection-system
cd anomalib-compact-inspection-system 
```

## CPU
```bash
pip install -r requirements.txt
```

## CUDA
```bash
pip install -r requirements.txt
```
これに追加してpytorchとtorchvisionをCUDAバージョンなどの環境に応じたものをインストールしてください。

Add to this by installing PyTorch and Torchvision versions that match your CUDA environment.

# 起動
```bash
cd anomalib-compact-inspection-system
python src/main.py
```

# 操作
* RUNボタンを押すと検査開始。もう一度RUNボタンを押すと検査停止
* 検査中、カメラ画像で異常スコアが判定しきい値（configファイルのinspection.judge_th）を超えると異常と判定する
* 検査中、異常判定（OK/NG）と画像全体に対する異常スコア（0～1）を表示する
* 検査中、局所領域ごとの異常スコア（異常マップ）をヒートマップ化してオーバーレイ表示する


# 設定ファイル(config.yaml)
```
title: Anomalib compact inspection system # アプリケーションのタイトル

ui:
  window_size: [1024, 600] # ウィンドウサイズ
  camlive_size: [640, 480] # カメラライブ画面の表示サイズ
  bg_color: [255, 255, 255] # ウィンドウ背景色

camera:
  id: 0 # カメラID

inspection:
  judge_th: 0.5 # 判定しきい値（この設定値異常のスコアの場合NGと判定する（0～1））

model:
  ckpt_path: "models/model.ckpt" # Anomalibで作成したモデルckptファイルのパス
  cfg_path: "models/config.yaml" # Anomalibで作成したモデルのconfigフィアルのパス
  gpu: False # GPUを有効化する場合True

visualize:
  cut_th: 0.4 # ヒートマップ可視化で可視化するAnomaly mapのしきい値（この値以下のスコアについては可視化しない）
  normalize: True　# ヒートマップを標準化する（Trueにすると出力を際立たせる）

save_image: # 学習データ取得のための付属機能。カメラライブ画面で表示されている画像を画像データとして保存する
　　　　　　 # 正常データ用と異常データ用の保存先を設定しておき、SAVE NORMAL(正常データ保存)ボタン、
　　　　　　 # SAVE ABNORMAL（異常データ保存）ボタンを押すと、それぞれの保存先に保存する
  enable: True # Trueで機能ON（SAVE NORMALボタンと, SAVE ABNORMALボタンを表示する。Falseでボタン非表示）
  normal_image_save_path: "save_images/normal" # 正常データとして保存する画像の保存フォルダパス
  abnormal_image_save_path: "save_images/abnormal" # 異常データとして保存する画像の保存フォルダパス

log:
  level: info # ログレベル（fatal, error, warn, info, debug）
```

