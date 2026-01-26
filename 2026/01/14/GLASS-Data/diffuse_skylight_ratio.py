# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import xarray as xr

def _load_da(nc_path: str, candidates: list[str]) -> xr.DataArray:
    """从 netCDF 里按候选变量名读取 DataArray。"""
    ds = xr.open_dataset(nc_path)
    for name in candidates:
        if name in ds.variables:
            return ds[name]
    raise KeyError(f"None of {candidates} found in {nc_path}. Available: {list(ds.variables)}")

def compute_diffuse_skylight_ratio_s(
    ndds_path: str,  # nddsfsfc monthly mean (near-IR diffuse downward)
    nbds_path: str,  # nbdsfsfc monthly mean (near-IR beam/direct downward)
    vdds_path: str,  # vddsfsfc monthly mean (visible diffuse downward)
    vbds_path: str,  # vbdsfsfc monthly mean (visible beam/direct downward)
    month: str | None = None,     # e.g. "2005-01"; None => compute for all times
    out_nc: str | None = None,    # e.g. "s_2005-01_1deg.nc" or "s_all.nc"
    regular_res_deg: float | None = 1.0,  # None => keep native (often Gaussian) grid
    fill_value: float = 0.5,      # total<=0 或缺失时填充（极夜区域无太阳）
) -> xr.DataArray:
    """
    计算 diffuse skylight ratio s。
    s = (NDDSF + VDDSF) / (NDDSF + VDDSF + NBDSF + VBDSF)

    返回：xarray.DataArray (dims: time?, lat, lon)
    """
    # 1) 读四个变量（兼容大小写）
    ndds = _load_da(ndds_path, ["nddsf", "NDDSF"])
    nbds = _load_da(nbds_path, ["nbdsf", "NBDSF"])
    vdds = _load_da(vdds_path, ["vddsf", "VDDSF"])
    vbds = _load_da(vbds_path, ["vbdsf", "VBDSF"])

    # 2) 对齐维度（time/lat/lon）
    ndds, nbds, vdds, vbds = xr.align(ndds, nbds, vdds, vbds, join="inner")

    # 3) 选月份（如果给了 month）
    if month is not None:
        t0 = pd.to_datetime(f"{month}-01")
        t1 = t0 + pd.offsets.MonthBegin(1)  # 下个月月初
        if "time" in ndds.dims:
            ndds = ndds.sel(time=slice(t0, t1)).isel(time=0)
            nbds = nbds.sel(time=slice(t0, t1)).isel(time=0)
            vdds = vdds.sel(time=slice(t0, t1)).isel(time=0)
            vbds = vbds.sel(time=slice(t0, t1)).isel(time=0)

    # 4) 计算 s
    diffuse = ndds + vdds
    direct  = nbds + vbds
    total   = diffuse + direct

    s = xr.where(total > 1e-6, diffuse / total, np.nan).clip(0.0, 1.0)

    # 5) lon 若为 0~360，转为 -180~180 并排序
    if "lon" in s.coords and float(s.lon.max()) > 180:
        lon_new = ((s.lon + 180) % 360) - 180
        s = s.assign_coords(lon=lon_new).sortby("lon")

    # 6) lat 排序（有些数据是从北到南）
    if "lat" in s.coords:
        s = s.sortby("lat")

    # 7) 可选：插值到规则经纬网（推荐：便于后续栅格重投影/匹配 500m）
    if regular_res_deg is not None:
        res = float(regular_res_deg)
        lon_t = np.arange(-180 + res/2, 180, res)
        lat_t = np.arange(-90 + res/2,  90, res)
        s = s.interp(lon=lon_t, lat=lat_t, method="linear")

    # 8) 缺失填充
    s = s.fillna(fill_value).astype(np.float32)
    s.name = "s"
    s.attrs["long_name"] = "diffuse skylight ratio"
    s.attrs["description"] = "s = (NDDSF+VDDSF)/(NDDSF+VDDSF+NBDSF+VBDSF)"
    s.attrs["range"] = "0..1"

    # 9) 保存
    if out_nc is not None:
        s.to_netcdf(out_nc)

    return s


if __name__ == "__main__":
    # ======= 改成你本地的 4 个 NCEP 月平均 nc 文件路径 =======
    ndds = r"/home/zhangpengwen/palwe/GLASS/NCEP/nddsf.sfc.mon.mean.nc"
    nbds = r"/home/zhangpengwen/palwe/GLASS/NCEP/nbdsf.sfc.mon.mean.nc"
    vdds = r"/home/zhangpengwen/palwe/GLASS/NCEP/vddsf.sfc.mon.mean.nc"
    vbds = r"/home/zhangpengwen/palwe/GLASS/NCEP/vbdsf.sfc.mon.mean.nc"

    # 例1：算 2005-01 的 s，并插值到 1°规则网格
    '''s_200501 = compute_diffuse_skylight_ratio_s(
        ndds, nbds, vdds, vbds,
        month="2005-01",
        out_nc="s_2005-01_1deg.nc",
        regular_res_deg=1.0
    )
    print(s_200501)'''

    #例2：算全部月份的 s（时间序列），并插值到 1°规则网格
    s_all = compute_diffuse_skylight_ratio_s(
        ndds, nbds, vdds, vbds,
        month=None,
        out_nc="s_all_1deg.nc",
        regular_res_deg=1.0
    )
