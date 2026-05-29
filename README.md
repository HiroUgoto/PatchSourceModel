# Hierarchical Friction Patch Source Model - Dataset Handler


A utility tool designed to efficiently manage, visualize, and export hierarchical friction-patch earthquake source models (including final slip distributions, patch configurations, and moment-rate functions) stored in HDF5 format.

HDF5形式にまとめられた階層型摩擦パッチ震源モデル（断層すべり分布、パッチ分布、モーメントレート関数）を効率的に管理・可視化・エクスポートするためのユーティリティツールです。

## Dataset

A dataset of hierarchical friction-patch earthquake source models (in HDF5 format) is available at the following Zenodo URL. 

階層型摩擦パッチ震源モデルのデータセット（HDF5フォーマット）は，以下のとおりZenodoから入手することができます．

[Dataset of Hierarchical Friction-Patch Source Models](https://doi.org/10.5281/zenodo.20319772)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20319772.svg)](https://doi.org/10.5281/zenodo.20319772)


## Citation

If you use this dataset or code in your research, please cite the following paper:

本データセットまたはコードを研究・論文等で使用する場合は、以下の論文を参照（引用）してください。

> **Hiroyuki Goto (2024)** Source scaling of simulated dynamic ruptures using hierarchical slip-weakening patch model, *Bulletin of the Seismological Society of America*, 114(2), 690-709. https://doi.org/10.1785/0120230174

## Folder Layout
```
.
├── LICENSE
├── README.md
├── requirements.txt
├── patchsourcemodel.py       
└── 01_model_selection.py     # Sample Script
```

## Usage

1. 準備
必要なライブラリをインストールします。

```
pip install -r requirements.txt
```

2. サンプルコード
以下のように、patchsourcemodel をインポートしてデータセットを操作します。

```python
import patchsourcemodel as psm

# データセットの初期化（HDF5ファイルのパスを指定）
dataset = psm.SourceModelDataset("hdf5/Model_fullspace_all_v01.h5")

# 指定したモーメントマグニチュード（Mw）に最も近いイベントを検索・取得
model = dataset.find_by_mw(target_mw=6.5)
print(f"Found Event ID: {model.id}, Mw: {model.mw:.2f}")

# モデルをプロットして確認する
model.plot_model()

# データのテキストエクスポート
model.export_mr_to_txt(output_dir="./output")
model.export_slipr_to_txt(output_dir="./output")
```

## License

MIT License

## Author

**Hiroyuki Goto** (Kyoto University)


