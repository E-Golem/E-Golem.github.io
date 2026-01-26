# -*- coding: utf-8 -*-
# GeoTIFF(12 bands) -> NetCDF4 (compressed) with 2D lat/lon (lazy via dask)
# 批量版：遍历目录下所有 tif，逐个输出 nc

import os
import glob
import numpy as np
import rasterio
from rasterio.windows import Window
import xarray as xr
import dask.array as da

data_dic = {3: "LAI12M", 2: "GREENFRAC", 1: "ALBEDO12M"}

# === 输入输出路径：改成目录批量 ===
tif_dir = "/home/zhangpengwen/palwe/GLASS/BlueSkyAlbedo_Yearly_wgs84"
nc_dir  = "/home/zhangpengwen/palwe/GLASS/BlueSkyAlbedo_Yearly_wgs84_nc"

varname = data_dic[1]       # 你选择的变量名（批量时保持不变）
nodata_value = -9999        # 缺测值
out_dtype = float           # 数据输出类型
coord_dtype = float         # 2D坐标输出类型（可改 np.float32 更省空间）

chunk_y = 1024
chunk_x = 1024

os.makedirs(nc_dir, exist_ok=True)

# === 用 Dask 懒加载：按 window 读取 GeoTIFF（避免一次性读入）===
class RasterioWindowReader:
    """
    让 dask 能通过 __getitem__ 分块读取 GeoTIFF：
    形状为 (band, y, x)，band 为 0-based，在内部转成 rasterio 的 1-based indexes。
    """
    def __init__(self, path, nodata, dtype, max_bands=None):
        self.path = path
        self.nodata = nodata
        self.dtype = np.dtype(dtype)
        with rasterio.open(path) as src:
            self.count = src.count if max_bands is None else min(src.count, max_bands)
            self.height = src.height
            self.width = src.width
        self.shape = (self.count, self.height, self.width)
        self.ndim = 3

    def __getitem__(self, key):
        if not isinstance(key, tuple) or len(key) != 3:
            raise IndexError("Expected key as (band, y, x) slices")

        bkey, rkey, ckey = key

        def _slice_to_start_stop_step(s, maxlen):
            if isinstance(s, slice):
                start = 0 if s.start is None else s.start
                stop = maxlen if s.stop is None else s.stop
                step = 1 if s.step is None else s.step
                return start, stop, step
            else:  # int
                return int(s), int(s) + 1, 1

        # bands
        if isinstance(bkey, slice):
            b0, b1, bstep = _slice_to_start_stop_step(bkey, self.count)
            band_ids = list(range(b0, b1, bstep))  # 0-based
        else:
            band_ids = [int(bkey)]
        indexes = [b + 1 for b in band_ids]  # rasterio 1-based

        # rows/cols
        r0, r1, rstep = _slice_to_start_stop_step(rkey, self.height)
        c0, c1, cstep = _slice_to_start_stop_step(ckey, self.width)

        window = Window.from_slices((r0, r1), (c0, c1))

        with rasterio.open(self.path) as src:
            arr = src.read(indexes=indexes, window=window, out_dtype=self.dtype)

        # nodata -> NaN
        arr = np.where(arr == self.nodata, np.nan, arr).astype(self.dtype, copy=False)

        # 若出现步长（一般不会），再做切片
        if rstep != 1 or cstep != 1:
            arr = arr[:, ::rstep, ::cstep]

        # 如果 band 是单个 int，返回 (y, x)
        if not isinstance(bkey, slice) and np.isscalar(bkey):
            arr = arr[0]

        return arr


tif_list = sorted(glob.glob(os.path.join(tif_dir, "*.tif")))
if not tif_list:
    raise FileNotFoundError(f"目录下未找到 tif：{tif_dir}")

for tiff_path in tif_list:
    base = os.path.splitext(os.path.basename(tiff_path))[0]
    nc_out = os.path.join(nc_dir, base + ".nc")

    # === 读取基础信息（不读全数据） ===
    with rasterio.open(tiff_path) as src:
        height, width = src.height, src.width
        band_count = src.count
        transform = src.transform
        crs = src.crs

    if band_count < 12:
        raise ValueError(f"{tiff_path} 波段数为 {band_count}，小于 12，无法组成 12 个月数据。")

    reader = RasterioWindowReader(tiff_path, nodata=nodata_value, dtype=out_dtype, max_bands=12)

    # 形状：(12, y, x)，chunks：(1, chunk_y, chunk_x)
    tif_dask = da.from_array(reader, chunks=(1, chunk_y, chunk_x), asarray=False, name="tif_stack")

    # 加 Time 维： (1, 12, y, x)
    data_4d = tif_dask[None, :, :, :]

    # === 生成 2D lon/lat（Dask 懒生成，不在内存里展开） ===
    a, b, c, d, e, f = transform.a, transform.b, transform.c, transform.d, transform.e, transform.f

    row2d = da.arange(height, chunks=chunk_y)[:, None]
    col2d = da.arange(width,  chunks=chunk_x)[None, :]

    lon2d = c + (col2d + 0.5) * a + (row2d + 0.5) * b
    lat2d = f + (col2d + 0.5) * d + (row2d + 0.5) * e

    lon2d = lon2d.astype(coord_dtype)
    lat2d = lat2d.astype(coord_dtype)

    # === 组装 xarray.Dataset ===
    ds = xr.Dataset(
        data_vars={
            varname: (("Time", "month", "south_north", "west_east"), data_4d)
        },
        coords={
            "Time": np.array([0], dtype=np.int32),
            "month": np.arange(1, 13, dtype=np.int16),
            "south_north": np.arange(height, dtype=np.int32),
            "west_east": np.arange(width, dtype=np.int32),
            "lon": (("south_north", "west_east"), lon2d),
            "lat": (("south_north", "west_east"), lat2d),
        },
        attrs={
            "description": f"{varname} 12-month stack from GeoTIFF with 2D lat/lon (lazy, compressed)",
            "source_geotiff": tiff_path,
            "crs_wkt": crs.to_wkt() if crs else "",
            "transform": tuple(transform),
            "nodata_value_in_tif": nodata_value,
            "note": "lat/lon are in the GeoTIFF CRS units; if CRS is projected, they are not geographic degrees.",
        }
    )

    ds = ds.chunk({
        "Time": 1,
        "month": 1,
        "south_north": chunk_y,
        "west_east": chunk_x
    })

    # === 压缩与写出 ===
    encoding = {
        varname: {
            "zlib": True,
            "complevel": 4,
            "shuffle": True,
            "dtype": "float32",
            "chunksizes": (1, 1, chunk_y, chunk_x),
        },
        "lon": {
            "zlib": True,
            "complevel": 4,
            "shuffle": True,
            "dtype": "float64" if coord_dtype == np.float64 else "float32",
            "chunksizes": (chunk_y, chunk_x),
        },
        "lat": {
            "zlib": True,
            "complevel": 4,
            "shuffle": True,
            "dtype": "float64" if coord_dtype == np.float64 else "float32",
            "chunksizes": (chunk_y, chunk_x),
        },
    }

    ds.to_netcdf(nc_out, engine="netcdf4", encoding=encoding)
    print(f"✅ {os.path.basename(tiff_path)} -> {nc_out}")

print("🎉 全部 tif 批量转换完成！")
