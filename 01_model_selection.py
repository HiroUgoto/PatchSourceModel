import patchsourcemodel as psm

HDF5_dir = "hdf5"
output_dir = "output"

# HDF5ファイルを読み込む
dataset = psm.SourceModelDataset(f"{HDF5_dir}/Model_fullspace_all_v01.h5")
dataset.extract_mw_list(plot=True)

# Mwから一番近いイベントを検索して取得（イベントオブジェクトが返る）
model = dataset.find_by_mw(target_mw=5.8)
print(f"Found ID: {model.id} with Mw: {model.mw:.2f}")

# モデルをプロットして確認する
model.plot_model()

# データを出力する
model.export_slipr_to_txt(output_dir="./output")
model.export_mr_to_txt(output_dir="./output")