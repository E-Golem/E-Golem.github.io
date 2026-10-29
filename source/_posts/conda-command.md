---
title: conda常用命令学习与记录
date: 2025-12-17 18:00
tags: [codna,command,python]
excerpt: conda常用命令学习
categories:
    - python
    - conda
banner_img: 
---

**记录部分常用conda指令：（持续更新）**

- conda list -n {环境名} {包名}  --列出指定环境包信息，不加环境名和包名就是列出当前环境所有包
- conda env list/conda info --envs  --查看环境
- conda env remove -n {环境名}  --删除环境
- conda clean -a  --删除环境后释放缓存
- conda install -c conda-forge {包名}  --使用conda-forge下载包
- conda activate {环境名}  --激活环境
- conda deactivate  --退出当前环境，如果不是base环境需要执行两次
- 