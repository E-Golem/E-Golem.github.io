---
title: 【GLASS ALBEDO MODIS 500m 数据集】的下载和处理
date: 2026-01-14 11:45:39
tags: [python,WRF]
excerpt: GLASS数据的下载和预处理（hdf转tif、栅格镶嵌、波段合成）
categories:
    - python
---

北师大全球陆表特征参量（GLASS）数据集，[简介](https://glass-product.bnu.edu.cn/) 
下载地址：[GLASS 数据集](https://glass.hku.hk/download.html)

原本WRF中用到的是MODIS ALBEDO，然而GLASS数据集空值更少，精度更好，因此将MODIS数据替换成GLASS数据会提升实验结果的可靠性。

下面介绍GLASS数据的处理的步骤

## 1、下载Albedo MODIS 500m数据

GLASS提供的数据集是hdf格式的地图瓦片，时间分辨率是8d，空间分辨率是500m，下载页数据按天数存储到对应的目录下，命名以瓦片编号区分。中国范围内的瓦片编号已经在脚本中提供。

## 2、地表反照率的计算

[参考文献](https://agupubs.onlinelibrary.wiley.com/doi/10.1002/2017JD027010)
计算公式
>**Albedo=(1-s)*\alpha_b+s*\alpha_w**  

*s*为太阳漫辐射漫射的比例，alpha_b为黑天反照率(BSA)，alpha_w为白天反照率(WSA)
对于GLASS数据，只需要用shortwave短波辐射计算即可（短波已经包含了可见光和近红外波段）
>*黑天反照率（Black-sky albedo）*：是指地表再仅有直射太阳光照射条件下的反照率；
>*白天反照率（White-sky albedo*：是指地表再全漫射光（如多云或阴天）条件下的反照率

*漫射天窗比*（S）：是漫射辐照度占辐射总量的比例  
 s =（漫射可见光+漫射红外）/（漫射可见光+漫射红外+直射可见光+直射红外）
使用NCEP数据进行计算[https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/surface_gauss/](https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/surface_gauss/)

代码如下：{% asset_path diffuse_skylight_ratio.py %}  

漫射天窗比计算结果如下：{% asset_img s.png 漫射天窗比 %}

之后根据公式计算蓝空反照率（包括hdf转化为tif、图像镶嵌、以及坐标系的转化）：

代码如下：{% asset_path hdf_monthly_to_tif.py %}

最终裁剪后的结果如下：{% asset_img bluesky.png 裁剪后的蓝空反照率数据，可以看出空值很少 %}

## 3、波段合成与转换成nc数据

这里使用的是qgis环境，qgis的安装用到了micromamba

波段合成代码：{% asset_path monthly_to_yearly_multiband.py %}

波段合成后的tif转nc代码：{% asset_path tif_to_nc.py %} ,不过这里是转换为压缩的netcdf4格式，如果是WRF中需要的netcdf classic则不能压缩，数据量会很大。

转化后的nc数据如下：{% asset_img nc.png 转换后的nc数据可视化 %}

至此GLASS数据处理完成，后续就是将nc数据替换到WRF中，即可进行后续的调参。
