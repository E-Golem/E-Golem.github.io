#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

from osgeo import gdal
gdal.UseExceptions()

# 你的固定命名规则：
# BlueSkyAlbedo_shortwave_200101_wgs84.tif
PAT = re.compile(r"^BlueSkyAlbedo_shortwave_(?P<ym>\d{6})_wgs84\.tif$", re.IGNORECASE)


def scan_monthly(in_dir: Path, recursive: bool):
    """
    返回: year_to_month_files[year][month] = Path
    """
    year_to_month_files = defaultdict(dict)

    files = in_dir.rglob("*.tif") if recursive else in_dir.glob("*.tif")
    for fp in files:
        if not fp.is_file():
            continue
        m = PAT.match(fp.name)
        if not m:
            continue

        ym = m.group("ym")
        year = int(ym[:4])
        month = int(ym[4:6])
        if not (1 <= month <= 12):
            continue

        # 同一年同月重复时保留第一个
        if month in year_to_month_files[year]:
            print(f"[WARN] duplicated {year}-{month:02d}, keep first, skip: {fp}")
            continue

        year_to_month_files[year][month] = fp

    return year_to_month_files


def check_compatible(ref_ds, ds, path):
    if ds.RasterCount != 1:
        raise RuntimeError(f"{path} has {ds.RasterCount} bands, expected 1.")
    if (ds.RasterXSize != ref_ds.RasterXSize) or (ds.RasterYSize != ref_ds.RasterYSize):
        raise RuntimeError(f"{path} size mismatch vs reference.")
    if ds.GetProjection() != ref_ds.GetProjection():
        raise RuntimeError(f"{path} projection mismatch vs reference.")
    if ds.GetGeoTransform() != ref_ds.GetGeoTransform():
        raise RuntimeError(f"{path} geotransform mismatch vs reference.")


def stack_one_year(year: int, month_map: dict, out_path: Path,
                   allow_partial: bool, overwrite: bool,
                   src_nodata=None,
                   compress="DEFLATE",
                   threads="ALL_CPUS"):
    months = sorted(month_map.keys())
    print(f'正在处理{year}年')
    if (not allow_partial) and months != list(range(1, 13)):
        missing = sorted(set(range(1, 13)) - set(months))
        print(f"[SKIP] {year}: missing months {', '.join([f'{m:02d}' for m in missing])}")
        return

    if out_path.exists() and (not overwrite):
        print(f"[SKIP] exists: {out_path}")
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 按月排序输入
    in_paths = [str(month_map[m]) for m in months]

    # 一致性检查（避免悄悄重采样/错位）
    ref_ds = gdal.Open(in_paths[0], gdal.GA_ReadOnly)
    if ref_ds is None:
        raise RuntimeError(f"Cannot open {in_paths[0]}")

    # 如果没显式给 nodata，就尝试从第一张读
    if src_nodata is None:
        b1 = ref_ds.GetRasterBand(1)
        nd = b1.GetNoDataValue()
        src_nodata = nd

    for p in in_paths[1:]:
        ds = gdal.Open(p, gdal.GA_ReadOnly)
        if ds is None:
            raise RuntimeError(f"Cannot open {p}")
        check_compatible(ref_ds, ds, p)

    # 临时 VRT
    vrt_path = out_path.with_suffix(".vrt")
    if vrt_path.exists():
        vrt_path.unlink()

    vrt_opts = gdal.BuildVRTOptions(
        separate=True,
        srcNodata=src_nodata,
        VRTNodata=src_nodata
    )
    vrt_ds = gdal.BuildVRT(str(vrt_path), in_paths, options=vrt_opts)
    if vrt_ds is None:
        raise RuntimeError(f"BuildVRT failed for {year}")
    vrt_ds = None

    # 输出 GeoTIFF
    creation_opts = [
        "TILED=YES",
        f"COMPRESS={compress}",
        "BIGTIFF=IF_SAFER",
        f"NUM_THREADS={threads}",
    ]

    if out_path.exists() and overwrite:
        out_path.unlink()

    translate_opts = gdal.TranslateOptions(
        format="GTiff",
        creationOptions=creation_opts,
        noData=src_nodata
    )
    gdal.Translate(str(out_path), str(vrt_path), options=translate_opts)

    # 写 band 描述（方便 QGIS 里看）
    ds_out = gdal.Open(str(out_path), gdal.GA_Update)
    if ds_out:
        for i, m in enumerate(months, start=1):
            band = ds_out.GetRasterBand(i)
            band.SetDescription(f"{year}-{m:02d}")
            band.SetMetadataItem("YEAR", str(year))
            band.SetMetadataItem("MONTH", f"{m:02d}")
        ds_out.FlushCache()
        ds_out = None

    # 清理 vrt
    try:
        vrt_path.unlink()
    except Exception:
        pass

    print(f"[OK] {year} -> {out_path} ({len(months)} bands)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", required=True, help="月尺度tif目录（包含 BlueSkyAlbedo_shortwave_YYYYMM_wgs84.tif）")
    ap.add_argument("--out-dir", required=True, help="输出目录")
    ap.add_argument("--recursive", action="store_true", help="递归扫描子目录")
    ap.add_argument("--allow-partial", action="store_true", help="允许缺月也合成（波段数=存在月数）")
    ap.add_argument("--overwrite", action="store_true", help="覆盖已存在输出（默认跳过）")
    ap.add_argument("--src-nodata", type=float, default=None, help="指定nodata（默认尝试从源数据读取）")
    ap.add_argument("--compress", default="DEFLATE", help="压缩：DEFLATE/LZW/NONE")
    ap.add_argument("--threads", default="ALL_CPUS", help="NUM_THREADS，例如 ALL_CPUS 或 8")
    args = ap.parse_args()

    in_dir = Path(args.in_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    year_map = scan_monthly(in_dir, args.recursive)
    if not year_map:
        print("[ERROR] No matching files found. Expect names like BlueSkyAlbedo_shortwave_YYYYMM_wgs84.tif")
        sys.exit(1)

    for year in sorted(year_map.keys()):
        out_name = f"BlueSkyAlbedo_shortwave_{year}.tif"
        out_path = out_dir / out_name
        stack_one_year(
            year=year,
            month_map=year_map[year],
            out_path=out_path,
            allow_partial=args.allow_partial,
            overwrite=args.overwrite,
            src_nodata=args.src_nodata,
            compress=args.compress,
            threads=args.threads
        )


if __name__ == "__main__":
    main()
