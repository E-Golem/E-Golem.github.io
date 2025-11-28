---
title: 学习Linux指令的记录
tags: [Linux,command]
date: 2025-9-18
excerpt: 学习Linux指令的记录，教程来源于菜鸟教程
banner_img: /img/Linux.jpg
categories: 
    - Linux
---

学习Linux指令的记录，教程来源于菜鸟[教程](https://www.runoob.com/markdown/md-tutorial.html)

# Linux Learning  

## 目录处理命令
- ls 列出目录和文件名
- cd 切换目录
- pwd 显示当前目录
- mkdir 创建新目录
- rmdir 删除空目录
- cp 复制
- rm 删除
- mv 移动或修改名称

## 文件查看命令
- cat 从第一行开始显示文件内容
- tac 与cat相反，从最后一行开始
- nl 显示文件输出行号
- more 按页显示文件内容
- less 可以往前翻页
- head 只看头几行
- tail 只看尾几行
  - -n接数字代表显示几行
  - -f表示持续侦测后面所接的档名

## 磁盘管理
- df文件系统的整体磁盘使用量
   - h 可读显示方式
   - T 文件系统类型
   - t 指定类型文件系统
   - i inode使用情况
   - H 1000b为单位
   - k kb显示
   - a 所有文件系统包括虚拟文件系统
     
- du 检查磁盘空间使用量
- fdisk 用于磁盘分区

---
## vi/vim的使用
### 命令模式
- i 输入模式
- x 删除字符
- ： 底线模式
- a 插入模式
- o 下方插入新行，进入插入模式
- O 上方插入新行，进入插入模式
- dd 剪切当前行
- yy 复制当前行
- p 粘贴到下方
- P 粘贴到上方
- u 撤销上一次
- ctrl + r 重做
- :w 保存文件
- :q 退出vim
- :ql 强制退出不保存
### 输入模式
ESC可返回普通模式
### 底线命令模式
- :w 保存文件
- :q 退出vim
- :wq 保存并退出
- :q！强制退出

![vim工作模式](https://www.runoob.com/wp-content/uploads/2014/07/vim-vi-workmodel.png)