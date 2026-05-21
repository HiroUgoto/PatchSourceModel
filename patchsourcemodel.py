"""
Hierarchical Friction Patch Source Model -- Dataset Handler

    If you use this dataset or code in your research, please cite the following paper:

    Hiroyuki Goto (2024) Source scaling of simulated dynamic ruptures using hierarchical slip-weakening patch model, 
    Bulletin of the Seismological Society of America*, 114(2), 690--709. https://doi:10.1785/0120230174

"""
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches, cm
from matplotlib.collections import PatchCollection


# ------------------------------------------------------------------------------------
class SourceModel:
    """1つの地震イベントのデータを保持し、操作するクラス"""
    def __init__(self, event_id, mw, slip, dx, mr, dt, filepath=None):
        self.id = event_id
        self.mw = mw
        self.slip = slip
        self.dx = dx
        self.mr = mr
        self.dt = dt
        self.filepath = filepath

    def plot_model(self):
        """3パネルプロットを実行するメソッド"""
        if self.filepath is None:
            raise ValueError("HDF5 filepath is not set. Cannot plot patch distribution.")

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
        
        nx, ny = self.slip.shape
        lx_km = (nx * self.dx) * 0.001
        ly_km = (ny * self.dx) * 0.001
        x_limit, y_limit = lx_km / 2, ly_km / 2
        extent = [-x_limit, x_limit, y_limit, -y_limit]

        # Panel 1: Slip
        im1 = ax1.imshow(self.slip.T, cmap='OrRd', extent=extent, aspect='equal')
        ax1.set_title(f'Slip Distribution\n(Mw: {self.mw:.2f})')
        ax1.set_xlabel('Strike (km)')
        ax1.set_ylabel('Dip (km)')
        fig.colorbar(im1, ax=ax1, label='Slip (m)', fraction=0.046, pad=0.04)

        # Panel 2: Patches
        with h5py.File(self.filepath, 'r') as f:
            grp = f[self.id]
            if 'dc' in grp:
                dc_grp = grp['dc']
                r_list = dc_grp['r_list'][:]
                nlevel = len(r_list)
                
                level_order = range(nlevel) if r_list[0] > r_list[-1] else range(nlevel-1, -1, -1)

                for n in level_order:
                    r_km = r_list[n] * 0.001
                    # 各レベルの座標をその場で読み込み
                    xs_km = dc_grp['xp'][f'level_{n}'][:] * 0.001
                    ys_km = dc_grp['yp'][f'level_{n}'][:] * 0.001

                    mask = (np.abs(xs_km) <= x_limit + r_km) & (np.abs(ys_km) <= y_limit + r_km)
                    f_xs, f_ys = xs_km[mask], ys_km[mask]
                    
                    level_color = cm.YlGn((nlevel-n)/nlevel)
                    patch_objs = [
                        patches.Circle(xy=(f_xs[i], f_ys[i]), radius=r_km, 
                                       fc=level_color, ec='black', lw=0.1, alpha=0.7)
                        for i in range(len(f_xs))
                    ]

                    if patch_objs:
                        pc = PatchCollection(patch_objs, match_original=True)
                        ax2.add_collection(pc)

        ax2.set_title(f'Patch Distribution (ID: {self.id})')
        ax2.set_xlabel('Strike (km)')
        ax2.set_xlim(-x_limit, x_limit)
        ax2.set_ylim(y_limit, -y_limit)
        ax2.set_aspect('equal')

        # Panel 3: Moment Rate
        time = np.arange(len(self.mr)) * self.dt
        ax3.plot(time, self.mr, color='firebrick', lw=1.5)
        ax3.set_title('Moment Rate Function')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Nm/s')
        ax3.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.show()

    def export_slipr_to_txt(self, output_dir="./output"):
        """
        HDF5ファイルから大容量の3D slip-rateデータをオンデマンドで読み込み、
        2D配列に整形してテキストファイルとして書き出します。
        """
        if self.filepath is None:
            raise ValueError("HDF5 filepath is not set. Cannot read slip-rate data.")

        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{self.id}.slipr")
        
        print(f"Loading and exporting slip-rate for ID: {self.id} ...")
        
        with h5py.File(self.filepath, mode='r') as f:
            slipr = f[self.id]['slip-rate'][:]

        # 3D配列 (nx, ny, nt) を 2D配列 (nx * ny, nt) に平坦化
        if slipr.ndim == 3:
            original_shape = slipr.shape
            slipr_2d = slipr.reshape(-1, original_shape[2])  
            print(f"  Reshaped array from {original_shape} to {slipr_2d.shape}.")
            
            # テキストファイルに出力
            np.savetxt(output_file, slipr_2d, fmt='%.6e', delimiter=' ')
            print(f"Export completed: {output_file}") 
        else:
            print(f"  [Warning] Expected 3D array for slip-rate, but got {slipr.ndim}D.")

    def export_mr_to_txt(self, output_dir="./output"):
        """
        すでにメモリ上に保持している moment-rate データをテキストファイルに書き出します。
        （ファイルへの再アクセスが発生しないため高速です）
        """
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{self.id}.mr")
        
        print(f"Exporting moment-rate for ID: {self.id} ...")
        
        np.savetxt(output_file, self.mr, fmt='%.6e', delimiter=' ')
        print(f"Export completed: {output_file}") 

# ------------------------------------------------------------------------------------
class SourceModelDataset:
    """HDF5ファイル全体を管理し、データ抽出を行うクラス"""
    def __init__(self, filepath):
        self.filepath = filepath
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"HDF5 file not found: {filepath}")

    def get_source_model(self, source_id):
        """指定したIDのソースモデルを読み込んで SourceModel オブジェクトを返す"""
        with h5py.File(self.filepath, 'r') as f:
            if source_id not in f:
                raise KeyError(f"Source ID {source_id} not found in dataset.")
            
            grp = f[source_id]
            mw = grp.attrs.get('mw', np.nan)
            slip = grp['slip'][:]
            dx = grp['slip'].attrs['dx']
            mr = grp['moment-rate'][:]
            dt = grp['moment-rate'].attrs['dt']
            
        return SourceModel(source_id, mw, slip, dx, mr, dt, self.filepath)

    def find_by_mw(self, target_mw):
        """最も指定したMwに近いソースモデルを検索して返す"""
        closest_id = None
        min_diff = float('inf')
        
        with h5py.File(self.filepath, 'r') as f:
            for group_name in f.keys():
                grp = f[group_name]
                if 'mw' in grp.attrs:
                    mw_val = grp.attrs['mw']
                    if not np.isnan(mw_val):
                        diff = abs(mw_val - target_mw)
                        if diff < min_diff:
                            min_diff = diff
                            closest_id = group_name
                            
        return self.get_source_model(closest_id)
    
    def extract_mw_list(self, output_file=None, plot=True):
        """全イベントのMwリストを抽出して返す"""
        mw_list = []
        with h5py.File(self.filepath, 'r') as f:
            for group_name in f.keys():
                grp = f[group_name]
                if 'mw' in grp.attrs:
                    mw_val = grp.attrs['mw']
                    if not np.isnan(mw_val):
                        mw_list.append((group_name, mw_val))

        if output_file is not None:
            with open(output_file, 'w') as out_f:
                for event_id, mw in mw_list:
                    out_f.write(f"{event_id}\t{mw:.2f}\n")

        if plot:
            bins,w = np.linspace(4,8,20,retstep=True)
            mw_centers = np.convolve(bins,np.array([0.5,0.5]),"valid")
            mw_hist,_ = np.histogram(mw_list,bins)
            nz_ind = np.nonzero(mw_hist)

            fig,ax1 = plt.subplots(figsize=(6,6))

            ax1.set_xlim([4.0,7.5])
            ax1.set_xticks([4,5,6,7])
            ax1.set_yscale('log')                
            ax1.plot(mw_centers[nz_ind],mw_hist[nz_ind],"-",c="firebrick",lw=1.5)
            ax1.errorbar(mw_centers[nz_ind],mw_hist[nz_ind],xerr=0.5*w,fmt='s',c="firebrick",elinewidth=0.8,ms=6,label="")
            ax1.set_xlabel("Mw")
            ax1.set_ylabel("Number of Events")
            ax1.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.show()

        return mw_list