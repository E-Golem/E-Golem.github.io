---
title: namelist.wps参数的修改与WPS运行
tags: [WRF,Linux]
date: 2025-10-07
excerpt: WPS的运行
banner_img: /img/wrf.png
categories: 
    - WRF
    - WPS

---
WPS参数的修改与运行

*****

### 1.namelist.wps参数的认识和修改

namelist文件是WPS模型的配置文件，主要分为四个部分：

![img](/img/wrf/wps/namelist.wps.png)

#### 1)**&share** 部分相当于通用设置

**wrf_core**:WRF的运行核心，根据需要设置，这里使用"ARW"
**max_dom**:数据的嵌套数，为1则为一层嵌套
**start_date;end_date**:输入的气象数据的时间起始区间
**interval_seconds**:气象数据的时间分辨率，单位为秒，21600即为六个小时
**io_form_geogrid**:geogrid的输出格式，1代表Binary，2代表netCDF，3代表GRIB1
**debug_level**:一个整数值，指示不同类型的消息应发送到标准输出的范围。当debug_level设置为0时，只有通常有用的消息和警告消息才会写入标准输出。当debug_level大于100时，提供更多运行时详细信息的信息性消息也会写入标准输出。调试消息和专门用于日志文件的消息从不写入标准输出，而是始终写入日志文件。默认值为0
  
#### 2)**&geogrid**：确定模拟区域，把各种地形数据集插值到模式格点上

**parent_id**:各个域的父域编号，最外层的父域是它本身，编号默认为1
**parent_grid_ratio**:嵌套域相较于父域的比例
**i_parent_start**:嵌套域在父域中的 i 起始位置
**j_parent_start**:嵌套域在父域中的 j 起始位置,即为嵌套域在父域中的相对位置
**e_we**:各域的东西向网格点数
**e_ns**:各域的南北向网格点数
**geog_data_res**:地理数据分辨率
**dx**:x方向网格间距
**dy**:y方向网格间距
**map_proj**:投影类型，中国范围内常使用lambert投影
**ref_lat**:参考纬度
**ref_lon**:参考经度
**truelat1**:第一真实纬度
**truelat2**:第二真实纬度（lambert投影是双标准纬线割圆锥投影）
**stand_lon**:标准经度
**pole_lat**:极地纬度
**pole_lon**:极地经度
**geog_data_path**：地理数据路径
**opt_geogrid_tbl_path**:Table文件输出路径
  
#### 3)**&ungrib**：控制 GRIB 数据提取到中间格式，再传递到metgrid程序

**out_format**：输出格式，默认为WPS
**prefix**：输出的文件前缀

#### 4)**&metgrid**:控制气象数据水平插值到 WRF 网格

**fg_name**：气象数据文件前缀
**io_form_metgrid**：输出数据的格式，同上，2代表输出.nc格式
**opt_output_from_metgrid_path**：输出路径

### 2.WPS的运行与数据的可视化

#### 1)运行geogrid.exe
确定模拟区域，把各种地形数据集插值到模式格点上

该步骤中输入数据为namelist.wps(用于确定范围和其他参数)，geog用来存放二进制的地表数据（地表反照率Albedo、植被覆盖度Greenfrac、叶面积指数LAI，土地利用Landuse），输出geo_em.d01.nc即为namelist确定的范围下包含各地形数据的格点。

使用ncview工具可以直接可视化nc数据

![geogrid输出](/img/wrf/wps/geo_em.d01.png)

#### 2)运行ungrib.exe
该程序是为了将grib格式的气象数据转化为中间文件，再传入到metgrid.exe插入气象数据建立气象场

运行该程序之前需要执行以下两个命令：
```bash
ln -sf ./ungrib/Variable_Tables/Vtable.ECMWF Vtable #生成table文件作为程序的输入,Vtable模板根据使用的气象数据选择，不同的table文件的作用是确定不同气象数据的提取方式
./link_grib.csh ./era5/2010*.grib #使用转换脚本将气象数据转换为中间格式
```
  
该步骤输入数据为上一步输出的nc数据、namelist.wps、命令行链接的Vtable，运行后输出下一步程序能够识别的中间文件
  
气象数据转化成以下格式
![气象数据](/img/wrf/wps/gribfile.png)
  
生成的中间文件如下图，'FILE'即为namelist设置的前缀
![ungrib生成中间文件](/img/wrf/wps/file.png)
  
#### 3)运行metgrid.exe
把气象场要素水平插值到geogrid模拟的范围内，生成气象场.nc数据

该步骤的输入数据是上一步生成的FILE文件、提取的气象场要素、namelist.wps，输出后续程序需要的nc数据，命名格式为**met_em.d01.{时间}.nc**

另外在该步骤中，还需要修改**METGRID.TBL**文件调整气象场要素的插值方式，这里笔者使用的默认文件，后续会学习如何修改该文件

![metgrid](/img/wrf/wps/met.png)