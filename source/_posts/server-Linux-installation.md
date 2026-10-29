---
title: 【Linux】服务器Linux系统的安装和配置
date: 2026-01-31 15:27:23
tags: [Linux]
excerpt: 介绍了服务器上Linux（Ubuntu）系统的安装和配置
categories:
    - Linux
---

课题组从学校申请到了一些服务器，这里总结一下对服务器系统进行重装和配置的过程

## 1、安装Linux系统

### 1.1 制作系统盘

需要一个空间大于8G的U盘，提前格式化。将镜像源文件iso下载后使用相关烤盘工具将系统烤到U盘中（如UltralSO）。

尽管是安装在服务器上，但是最好也是使用桌面端，因为相关配置在使用图形化界面是会更直观和方便  

这里使用的是***ubuntu20.04.6 desktop***版（较稳定版本，非最新）

### 1.2 安装系统

将外设（键鼠、显示器等）以及U盘插入服务器接口

- F11 进入boot menu
- 选择系统U盘进入安装界面（UEFI前缀）
- 选择oem installation方式（默认安装可能会出现问题）
- 没有什么特殊需求的话，选项基本都是默认
- 最后设置自己的用户名和密码（用户名和主机名使用oem是默认为oem的，后续安装完成后可以进行修改）

这个过程中没有网络，需要进入系统后在设置-网络中进行配置
配置项：IP地址、子网掩码、DNS、关网IP地址

可使用ping指令来检测ip配置是否成功

## 2、 SSH配置

之后进行ssh的配置

```bash
sudo apt update
sudo apt full-upgrade -y
#这里是由于前面安装时无网络，很多需要网络下载的组件在系统安装时没有装上，这里手动安装一下
sudo apt install openssh-server
sudo apt-get install telnet
sudo apt-get install nmap 
#安装端口连接软件
sudo ufw status 
#查看端口状态
sudo ufw enable
sudo ufw allow 22/tcp 
#开放某个端口，默认22是开放的
```

依次执行上面的指令

之后即可在远端连接ssh

## 3、可能遇到的问题

由于有的服务器可能存在硬件问题，因此需要排查

## 4、硬盘扩充

由于容量不太够，因此要进行硬盘的扩充，由于这里硬盘是RAID阵列，需要对硬盘进行配置才能被正确识别并使用

RAID是指一种硬盘存储技术，RAID1是指由两块相同的硬盘，将一个硬盘经乡道另一个硬盘上作为备份，用一半容量换更高的数据安全性

这里要用到 **StorCLI** ，它是RAID控制器的配置和监控工具，允许你在操作系统内查看、配置和管理你的 硬件**RAID**阵列

首先安装**StorCLI**（apt无法下载，需离线安装）

查看硬盘状态

```bash
sudo /opt/MegaRAID/storcli/storcli64 /c0 /eall /sall show
sudo /opt/MegaRAID/storcli/storcli64 /c0 /vall show
```

清除Foreign,Foreign是指物理硬盘上存在以前的RAID配置，需要先清除再创建新的虚拟磁盘

```bash
sudo /opt/MegaRAID/storcli/storcli64 /c0 /fall delete
```

创建新单盘VD（UGood可创建，意思是空闲）

```bash
sudo /opt/MegaRAID/storcli/storcli64 /c0 add vd type=raid0 drives=252:3 #（硬盘位置）
```

查看磁盘状态

```bash
lsblk -d -o NAME,MODEL,SIZE,TYPE
```

NFS文件共享，自动挂载修改fstab文件

sudo ufw allow 6819/tcp 主节点开放端口
sudo ufw disable 关闭防火墙（每个计算节点都要执行）
sinfo 查看slurm配置

slurm的配置
/etc/hosts 写入
munge.key
master端slurm的安装
client端slurm的安装
ssh密钥生成，免密ssh
munge -n | ssh node1 unmunge 测试

完成cu05的测试（成功）

id -u munge
id -g munge
必须调整为一致
需要把占位的程序移动到其他位置

修改service模式从forking到simple，更加稳定

计算节点动态库的识别（可能遇到的问题）
