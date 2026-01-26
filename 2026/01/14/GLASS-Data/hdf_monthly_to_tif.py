#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLASS Albedo (HDF) -> 月尺度短波 Blue-sky Albedo (GeoTIFF)

新增功能：
1) 断点续跑：自动跳过已生成的 tile/月 mosaics（可用 --overwrite 强制重算）
2) 防中断：捕获 Ctrl+C / SIGTERM，采用原子写入（.tmp -> replace），避免生成损坏文件

仅使用 3 个短波子数据集（按你第一张图为准）：
- ABD_BSA_shortwave
- ABD_WSA_shortwave
- ABD_QA_shortwave

蓝天反照率：
    BlueSky = (1 - s) * BSA + s * WSA
"""

import os
import re
import glob
import argparse
import datetime as dt
import signal
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
import xarray as xr
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.merge import merge as rio_merge


# -----------------------------
# 固定使用的短波子数据集名（按你第一张图为准）
# -----------------------------
BSA_FIELD = "ABD_BSA_shortwave"
WSA_FIELD = "ABD_WSA_shortwave"
QA_FIELD  = "ABD_QA_shortwave"


# -----------------------------
# 防中断：收到信号后设置停止标志
# -----------------------------
STOP_REQUESTED = False

def _handle_stop_signal(signum, frame):
    global STOP_REQUESTED
    STOP_REQUESTED = True
    print("\n[STOP] 收到中断信号，将在完成当前步骤后安全退出（已生成结果会保留）。")

signal.signal(signal.SIGINT, _handle_stop_signal)
signal.signal(signal.SIGTERM, _handle_stop_signal)


# -----------------------------
# 文件名解析：日期 / tile
# 示例：GLASS02E01.V50.A2019001.h23v04.2020165.hdf
# -----------------------------
RE_A = re.compile(r"\.A(\d{4})(\d{3})\.")
RE_TILE = re.compile(r"\.h(\d{2})v(\d{2})\.")

def parse_date_from_name(fname: str) -> dt.date:
    m = RE_A.search(fname)
    if not m:
        raise ValueError(f"无法解析 AYYYYDDD: {fname}")
    y = int(m.group(1))
    doy = int(m.group(2))
    return dt.date(y, 1, 1) + dt.timedelta(days=doy - 1)

def parse_tile_from_name(fname: str) -> str:
    m = RE_TILE.search(fname)
    if not m:
        raise ValueError(f"无法解析 hXXvYY: {fname}")
    return f"h{m.group(1)}v{m.group(2)}"


# -----------------------------
# HDF 子数据集读取（rasterio/GDAL 需支持 HDF4/HDF-EOS）
# -----------------------------
def get_subdataset_dict(hdf_path: str) -> Dict[str, str]:
    with rasterio.open(hdf_path) as ds:
        subs = ds.subdatasets
    return {s.split(":")[-1]: s for s in subs}

def read_subdataset(hdf_path: str, subdict: Dict[str, str], field: str) -> Tuple[np.ndarray, dict]:
    if field not in subdict:
        avail = sorted(subdict.keys())
        raise KeyError(
            f"文件 {os.path.basename(hdf_path)} 中找不到子数据集 '{field}'。\n可用子数据集：{avail}"
        )
    with rasterio.open(subdict[field]) as ds:
        arr = ds.read(1)
        profile = ds.profile
    return arr, profile


# -----------------------------
# QA 解码（按你给的 bit 规则）
# -----------------------------
def decode_glass_qa(qa: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    qa_u16 = qa.astype(np.uint16)
    overall = qa_u16 & np.uint16(0b11)                    # bits 0-1
    land    = (qa_u16 >> np.uint16(2)) & np.uint16(0x7F)  # bits 2-8
    good    = (qa_u16 >> np.uint16(9)) & np.uint16(0x7F)  # bits 9-15
    return overall.astype(np.uint8), land.astype(np.uint8), good.astype(np.uint8)

def build_qa_mask(
    qa: np.ndarray,
    qa_fill_value: int = 65535,
    overall_max: int = 1,
    land_min: int = 0,
    good_min: int = 0
) -> np.ndarray:
    mask = np.zeros(qa.shape, dtype=bool)

    mask |= (qa == qa_fill_value)

    overall, land, good = decode_glass_qa(qa)

    # 异常值保护
    mask |= (land > 100) | (good > 100)

    # 总体质量过滤
    mask |= (overall > overall_max)

    if land_min > 0:
        mask |= (land < land_min)
    if good_min > 0:
        mask |= (good < good_min)

    return mask


# -----------------------------
# 读取 s（月尺度 NetCDF），并构建 EPSG:4326 的“源栅格”
# -----------------------------
def open_s_nc(s_nc: str) -> xr.DataArray:
    ds = xr.open_dataset(s_nc)
    da = ds["s"] if "s" in ds.data_vars else ds[list(ds.data_vars)[0]]

    if "latitude" in da.dims and "lat" not in da.dims:
        da = da.rename({"latitude": "lat"})
    if "longitude" in da.dims and "lon" not in da.dims:
        da = da.rename({"longitude": "lon"})

    if float(da.lon.max()) > 180:
        lon_new = ((da.lon + 180) % 360) - 180
        da = da.assign_coords(lon=lon_new).sortby("lon")

    return da

def s_month_as_raster(s_da: xr.DataArray, year: int, month: int) -> Tuple[np.ndarray, rasterio.Affine, str]:
    t = np.datetime64(f"{year:04d}-{month:02d}-01")
    sm = s_da.sel(time=t, method="nearest") if "time" in s_da.dims else s_da

    sm = sm.sortby("lat", ascending=False).sortby("lon")

    lats = sm["lat"].values
    lons = sm["lon"].values
    if len(lons) < 2 or len(lats) < 2:
        raise ValueError("s 网格太小，无法推导分辨率。")

    resx = float(abs(lons[1] - lons[0]))
    resy = float(abs(lats[0] - lats[1]))

    west  = float(lons.min()) - resx / 2.0
    north = float(lats.max()) + resy / 2.0
    transform = rasterio.transform.from_origin(west, north, resx, resy)

    s_arr = sm.values.astype(np.float32)
    s_arr = np.where(np.isfinite(s_arr), s_arr, 0.5).astype(np.float32)

    return s_arr, transform, "EPSG:4326"

def reproject_s_to_profile(
    s_arr: np.ndarray,
    s_transform: rasterio.Affine,
    s_crs: str,
    target_profile: dict,
) -> np.ndarray:
    dst = np.empty((target_profile["height"], target_profile["width"]), dtype=np.float32)
    dst.fill(np.nan)

    reproject(
        source=s_arr,
        destination=dst,
        src_transform=s_transform,
        src_crs=s_crs,
        dst_transform=target_profile["transform"],
        dst_crs=target_profile["crs"],
        resampling=Resampling.bilinear,
        src_nodata=None,
        dst_nodata=np.nan
    )

    dst = np.where(np.isfinite(dst), dst, 0.5).astype(np.float32)
    dst = np.clip(dst, 0.0, 1.0)
    return dst


# -----------------------------
# 原子写 GeoTIFF：先写 tmp，再 replace，避免中断生成坏文件
# -----------------------------
def write_tif_atomic(path: str, arr: np.ndarray, profile: dict, nodata: float):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"

    # 如果上次中断留下 tmp，先删掉
    if os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    prof = profile.copy()
    prof.update(
        driver="GTiff",
        dtype=rasterio.float32,
        count=1,
        nodata=nodata,
        compress="deflate",
        tiled=True,
        bigtiff="IF_SAFER"
    )

    with rasterio.open(tmp_path, "w", **prof) as dst:
        dst.write(arr.astype(np.float32), 1)

    # 原子替换
    os.replace(tmp_path, path)


# -----------------------------
# 单 tile 月合成：直接累加 BlueSky（简洁）
# -----------------------------
def monthly_bluesky_tile(
    hdf_list: List[str],
    s_month_arr: np.ndarray,
    s_month_transform: rasterio.Affine,
    s_month_crs: str,
    scale_factor: float,
    valid_max_raw: int,
    nodata_out: float,
    qa_overall_max: int,
    qa_land_min: int,
    qa_good_min: int,
) -> Tuple[np.ndarray, dict]:
    if not hdf_list:
        raise RuntimeError("该 tile-月份没有文件。")

    # 用第一景拿 profile，并把 s 重投影到 tile 网格（该 tile 的当月固定）
    sub0 = get_subdataset_dict(hdf_list[0])
    _, prof0 = read_subdataset(hdf_list[0], sub0, BSA_FIELD)
    s_tile = reproject_s_to_profile(s_month_arr, s_month_transform, s_month_crs, prof0)

    sum_alb = np.zeros((prof0["height"], prof0["width"]), dtype=np.float64)
    cnt     = np.zeros((prof0["height"], prof0["width"]), dtype=np.uint16)

    for p in hdf_list:
        if STOP_REQUESTED:
            break

        subd = get_subdataset_dict(p)

        bsa_raw, _ = read_subdataset(p, subd, BSA_FIELD)
        wsa_raw, _ = read_subdataset(p, subd, WSA_FIELD)
        qa_raw,  _ = read_subdataset(p, subd, QA_FIELD)

        # 值域/填充值过滤（BSA/WSA int16，fill=-1 会被 <0 捕捉）
        mask = (bsa_raw < 0) | (wsa_raw < 0) | (bsa_raw > valid_max_raw) | (wsa_raw > valid_max_raw)

        # QA 过滤
        mask |= build_qa_mask(
            qa=qa_raw,
            qa_fill_value=65535,
            overall_max=qa_overall_max,
            land_min=qa_land_min,
            good_min=qa_good_min
        )

        bsa = np.where(mask, np.nan, bsa_raw.astype(np.float32)) * scale_factor
        wsa = np.where(mask, np.nan, wsa_raw.astype(np.float32)) * scale_factor

        alb = (1.0 - s_tile) * bsa + s_tile * wsa

        good = np.isfinite(alb)
        sum_alb[good] += alb[good]
        cnt[good] += 1

    alb_mean = np.where(cnt > 0, sum_alb / cnt, nodata_out).astype(np.float32)
    return alb_mean, prof0


# -----------------------------
# tile 拼接为整月 mosaics（原子写）
# -----------------------------
def mosaic_tiles_atomic(tile_tifs: List[str], out_tif: str, nodata: float):
    os.makedirs(os.path.dirname(out_tif), exist_ok=True)
    tmp_out = out_tif + ".tmp"

    if os.path.exists(tmp_out):
        try:
            os.remove(tmp_out)
        except Exception:
            pass

    srcs = [rasterio.open(p) for p in tile_tifs]
    try:
        mosaic, out_trans = rio_merge(srcs, nodata=nodata)
        out_meta = srcs[0].meta.copy()
        out_meta.update({
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
            "nodata": nodata,
            "dtype": "float32",
            "compress": "deflate",
            "tiled": True,
            "bigtiff": "IF_SAFER"
        })
        with rasterio.open(tmp_out, "w", **out_meta) as dst:
            dst.write(mosaic.astype(np.float32))
    finally:
        for s in srcs:
            s.close()

    os.replace(tmp_out, out_tif)


# -----------------------------
# 建立按月 & tile 索引：glass_root/YYYY/DDD/*.hdf
# -----------------------------
def build_month_index(glass_root: str, year0: int, year1: int) -> Dict[Tuple[int, int], Dict[str, List[str]]]:
    month_map = defaultdict(lambda: defaultdict(list))

    for y in range(year0, year1 + 1):
        ydir = os.path.join(glass_root, str(y))
        if not os.path.isdir(ydir):
            continue

        hdfs = glob.glob(os.path.join(ydir, "*", "*.hdf"))
        for p in hdfs:
            bn = os.path.basename(p)
            try:
                d = parse_date_from_name(bn)
                tile = parse_tile_from_name(bn)
            except Exception:
                continue
            month_map[(d.year, d.month)][tile].append(p)

    for ym in month_map:
        for tile in month_map[ym]:
            month_map[ym][tile].sort(key=lambda p: parse_date_from_name(os.path.basename(p)))

    return month_map


# -----------------------------
# 主程序
# -----------------------------
def main():
    DEFAULT_GLASS_ROOT = "/home/zhangpengwen/palwe/GLASS/Albedo/"
    DEFAULT_S_NC       = "/home/zhangpengwen/palwe/GLASS/s_all_1deg.nc"  # <- 改成你的 s.nc
    DEFAULT_OUT_DIR    = "/home/zhangpengwen/palwe/GLASS/BlueSkyAlbedo_Monthly"

    ap = argparse.ArgumentParser(description="GLASS 短波月尺度 Blue-sky Albedo（含 QA + 断点续跑 + 防中断）")

    ap.add_argument("--glass_root", default=DEFAULT_GLASS_ROOT, help="GLASS/Albedo 根目录（含年份子目录）")
    ap.add_argument("--s_nc", default=DEFAULT_S_NC, help="月尺度 s(NetCDF) 路径")
    ap.add_argument("--out_dir", default=DEFAULT_OUT_DIR, help="输出目录")

    ap.add_argument("--year0", type=int, default=2005)
    ap.add_argument("--year1", type=int, default=2006)

    ap.add_argument("--scale", type=float, default=1e-4, help="scale_factor，默认 0.0001")
    ap.add_argument("--valid_max_raw", type=int, default=10000, help="原始有效值最大值，默认 10000")
    ap.add_argument("--nodata", type=float, default=-9999.0, help="输出 nodata")

    ap.add_argument("--qa_overall_max", type=int, default=1, help="总体质量允许最大值：1=只保留 0/1")
    ap.add_argument("--qa_land_min", type=int, default=0, help="陆地比例阈值(0..100)，默认 0=不筛")
    ap.add_argument("--qa_good_min", type=int, default=0, help="好/可接受比例阈值(0..100)，默认 0=不筛")

    # 断点续跑相关
    ap.add_argument("--overwrite", action="store_true", help="强制覆盖已有输出（默认会跳过已生成结果）")

    args = ap.parse_args()

    # 1) 建立月度索引
    month_map = build_month_index(args.glass_root, args.year0, args.year1)
    if not month_map:
        raise RuntimeError(f"在 {args.glass_root} 没找到任何 HDF，请检查目录结构是否为 YYYY/DDD/*.hdf")

    # 2) 读取 s.nc
    s_da = open_s_nc(args.s_nc)

    # 3) 按月处理
    for (y, m) in sorted(month_map.keys()):
        if STOP_REQUESTED:
            print("[STOP] 已请求停止，退出主循环。")
            break

        out_month = os.path.join(args.out_dir, f"BlueSkyAlbedo_shortwave_{y}{m:02d}.tif")

        # (1) 月结果已存在 -> 跳过
        if (not args.overwrite) and os.path.exists(out_month):
            print(f"\n=== 跳过 {y}-{m:02d}（月结果已存在） ===")
            continue

        print(f"\n=== 处理 {y}-{m:02d} ===")

        # 当月 s（EPSG:4326）
        s_arr, s_tr, s_crs = s_month_as_raster(s_da, y, m)

        # 临时目录：保存每个 tile 的结果，便于断点续跑
        month_tmp = os.path.join(args.out_dir, "_tmp", f"{y}{m:02d}")
        os.makedirs(month_tmp, exist_ok=True)

        # 清理可能残留的 .tmp（不影响断点续跑）
        for p in glob.glob(os.path.join(month_tmp, "*.tmp")):
            try:
                os.remove(p)
            except Exception:
                pass

        # 逐 tile 处理
        expected_tiles = sorted(month_map[(y, m)].keys())
        tile_outs = []

        for tile in expected_tiles:
            if STOP_REQUESTED:
                print("[STOP] 已请求停止，结束本月 tile 处理。")
                break

            out_tile = os.path.join(month_tmp, f"BlueSky_{y}{m:02d}_{tile}.tif")

            # (2) tile 已存在 -> 跳过
            if (not args.overwrite) and os.path.exists(out_tile):
                print(f"  - 跳过 tile {tile}（已存在）")
                tile_outs.append(out_tile)
                continue

            hdfs = month_map[(y, m)][tile]

            try:
                alb_tile, prof = monthly_bluesky_tile(
                    hdf_list=hdfs,
                    s_month_arr=s_arr,
                    s_month_transform=s_tr,
                    s_month_crs=s_crs,
                    scale_factor=args.scale,
                    valid_max_raw=args.valid_max_raw,
                    nodata_out=args.nodata,
                    qa_overall_max=args.qa_overall_max,
                    qa_land_min=args.qa_land_min,
                    qa_good_min=args.qa_good_min,
                )

                # 原子写出 tile tif（防中断）
                write_tif_atomic(out_tile, alb_tile, prof, nodata=args.nodata)
                print(f"  - 完成 tile {tile}")
                tile_outs.append(out_tile)

            except Exception as e:
                # tile 出错：不中断整个脚本，方便后续修复后继续跑
                print(f"  [WARN] tile {tile} 处理失败：{e}")
                # 不加入 tile_outs，避免月拼接生成“缺块”结果

        # 如果中断了，就不做月拼接（下次可继续）
        if STOP_REQUESTED:
            print("[STOP] 中断请求已触发：本次不进行月拼接，已完成的 tile 结果已保留。")
            break

        # (3) 只在 tile 全部齐全时才拼接月 mosaics（避免生成缺块月产品）
        # 重新确认当月应有的 tile 是否都已存在
        all_exist = True
        final_tile_list = []
        for tile in expected_tiles:
            p = os.path.join(month_tmp, f"BlueSky_{y}{m:02d}_{tile}.tif")
            if os.path.exists(p):
                final_tile_list.append(p)
            else:
                all_exist = False

        if not all_exist:
            print(f"[WARN] {y}-{m:02d} 有 tile 未完成/缺失，本次不生成月拼接。下次重跑会自动续上。")
            continue

        # 月拼接：原子写
        mosaic_tiles_atomic(final_tile_list, out_month, nodata=args.nodata)
        print(f"保存：{out_month}")

    print("\n脚本结束。")


if __name__ == "__main__":
    main()


