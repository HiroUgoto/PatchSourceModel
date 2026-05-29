import patchsourcemodel as psm

HDF5_dir = "hdf5"
output_dir = "output"

# データセットの初期化（HDF5ファイルのパスを指定）
dataset = psm.SourceModelDataset(f"{HDF5_dir}/Model_fullspace_all_v01.h5")
# dataset.extract_mw_list(plot=True)

# 指定したモーメントマグニチュード（Mw）に最も近いイベントを検索・取得
model = dataset.find_by_mw(target_mw=6.2)
print(f"Found ID: {model.id} with Mw: {model.mw:.2f}")

# モデルをプロットして確認する
model.plot_model()

# データのテキストエクスポート
model.export_slipr_to_txt(output_dir="./output")
model.export_mr_to_txt(output_dir="./output")