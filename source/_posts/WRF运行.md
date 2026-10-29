---
title: WRF运行
date: 2026-03-16 20:58:58
tags:[WRF,Linux]
tages: [Linux,WRF]
excerpt: 【WRF】记录WRF的运行过程，包括namelist的设置
---

## 1、namelist.input的设置

WRF中提供了能够去除部分输出变量，或者加入部分输出变量

在&time_control中添加：

```namelist
iofields_filename                   = "heatwave_io.txt",
ignore_iofields_warning             = .true.,
```

其中iofields_filename是文本文件形式，写入需要添加或者去除的变量，比如可以使用下面的语句：

```text
# 剔除三维风场、垂直速度、各种水成物和高空扰动气压
-:h:0:U,V,W,QVAPOR,QCLOUD,QRAIN,QICE,QSNOW,PH,PHB,P,PB
```

去除研究中无用、同时及其占用空间的三维变量，节省空间

当然，对于WRF默认不输出的变量，也可以通过相似的命令添加到输出中

下面是WRF官方手册中的说明：

WRF也可以通过气象诊断功能计算日最高温和最低温并输出，省去手动计算的麻烦