import patchsourcemodel as psm

HDF5_dir = "hdf5"
output_dir = "output"

# データセットの初期化（HDF5ファイルのパスを指定）
dataset = psm.SourceModelDataset(f"{HDF5_dir}/Model_fullspace_all_v01.h5")

# 指定したMwの範囲のIDリストを取得
target_min, target_max = 6.3, 6.5
id_list = dataset.get_id_by_mw_range(target_min, target_max)

total_count = len(id_list)
print(f"Found {total_count} events between Mw {target_min} and {target_max}.")

for i, event_id in enumerate(id_list):
    model = dataset.get_source_model(event_id)

    print(f" [{i+1}/{total_count}] Processing ID: {model.id} (Mw: {model.mw:.2f})")

    # model.plot_model()
    # model.export_mr_to_txt(output_dir=output_dir)
