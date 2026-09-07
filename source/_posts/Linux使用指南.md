---
title: Linux使用指南
date: 2026-09-07 11:00:12
tags:
  - Linux
  - WRF
categories:
  - Linux
---

# Linux 使用指南

> 面向测绘工程 / 大气科学（WRF 数值模拟）方向研究生
> 系统平台：Ubuntu（20.04 / 22.04 / 24.04）
> 说明：本文所有命令均为真实可用的标准命令，涵盖基础指令、软件安装、系统管理、并行计算、科学计算（netCDF/HDF5）、WRF 实战以及求职应试高频考点。命令请结合实际环境核对参数后再执行。


<!-- more -->
---

## 目录

- 第一部分 基础篇
  - 1. Linux 概述与文件系统
  - 2. 命令行基础与 Shell
  - 3. 文件与目录操作
  - 4. 文本查看与处理
  - 5. 文件查找
  - 6. 文件压缩与归档
  - 7. 用户与权限管理
  - 8. 环境变量与 Shell 配置
  - 9. 网络与远程连接
- 第二部分 系统管理与软件安装
  - 10. 进程管理与系统监控
  - 11. 系统信息与硬件
  - 12. 磁盘与文件系统
  - 13. 服务管理与定时任务
  - 14. 软件安装（apt / 源码 / conda / pip）
- 第三部分 文本处理与脚本编程
  - 15. grep / sed / awk 与正则表达式
  - 16. Vim 编辑器
  - 17. Shell 脚本编程
- 第四部分 并行计算与科学计算
  - 18. 高性能计算基础
  - 19. OpenMP 共享内存并行
  - 20. MPI 分布式并行
  - 21. SLURM 作业调度系统
  - 22. 环境模块 module
  - 23. 科学计算库与数据工具
  - 24. WRF 模型实战
- 第五部分 求职与应试篇
  - 25. 高频面试考点
  - 26. 常用命令速查表

---

# 第一部分 基础篇

## 1. Linux 概述与文件系统

### 1.1 什么是 Linux

Linux 是一款开源的类 Unix 操作系统内核（Kernel），1991 年由 Linus Torvalds 发布。通常所说的"Linux 系统"是"内核 + GNU 工具集 + 发行版"的组合。常见发行版：
- Debian 系：Ubuntu、Debian、Linux Mint —— 使用 `apt` 包管理
- RedHat 系：CentOS、RHEL、Fedora —— 使用 `yum`/`dnf` 包管理
- SUSE 系：openSUSE、SLES —— 使用 `zypper`
- Arch 系：Arch Linux、Manjaro —— 使用 `pacman`

**为什么科研（WRF）要用 Linux**：
- 免费开源，数值模式（WRF、WRF-Chem、CMAQ）官方支持 Linux
- 强大的 Shell 脚本能力，便于批量处理与自动循环
- 适合高性能计算（HPC）集群，多节点并行
- 稳定、资源占用低、权限控制清晰
- 大量科研工具（NCL、CDO、netCDF 工具、Fortran 编译器）原生支持

### 1.2 Shell 与终端

- **终端（Terminal）**：人机交互的窗口程序
- **Shell**：解释执行命令的程序，常见 Bash（Ubuntu 默认）、Zsh、Sh、Tcsh
- 查看当前 Shell：`echo $SHELL`
- 查看系统默认 Shell：`cat /etc/passwd | grep $(whoami)`

### 1.3 文件系统层次标准（FHS）

Linux 一切皆文件。常用目录：

| 目录 | 用途 |
|---|---|
| `/` | 根目录，所有文件的起点 |
| `/home` | 普通用户家目录（如 `/home/zhangsan`） |
| `/root` | 超级用户（root）家目录 |
| `/etc` | 系统配置文件 |
| `/bin`、`/sbin` | 系统可执行命令（sbin 多为管理员命令） |
| `/usr` | 系统软件与库（`/usr/local` 常为手动安装软件目录） |
| `/var` | 可变数据，如日志 `/var/log`、缓存 `/var/cache` |
| `/tmp` | 临时文件，重启可能清空 |
| `/opt` | 第三方大型软件 |
| `/dev` | 设备文件（硬盘、终端等） |
| `/proc` | 虚拟文件系统，内存中的系统与进程信息 |
| `/sys` | 内核与硬件信息虚拟文件系统 |
| `/mnt`、`/media` | 挂载点（U 盘、光盘等） |

**路径概念**：
- 绝对路径：从根目录开始，如 `/home/user/test.nc`
- 相对路径：相对当前目录，如 `./test.nc`、`../data/`
- `.` 当前目录；`..` 上一级目录；`~` 当前用户家目录；`-` 上一次所在目录
- 使用 `pwd` 查看当前绝对路径

---

## 2. 命令行基础与 Shell

### 2.1 命令格式

```
命令 [选项] [参数]
```

- `ls -la /home`：`ls` 是命令，`-l`、`-a` 是选项，`/home` 是参数
- 短选项合并：`ls -la` 等价于 `ls -l -a`
- 长选项：`ls --all --long`

### 2.2 常用快捷键（Bash）

| 快捷键 | 作用 |
|---|---|
| `Tab` | 命令/文件名/路径自动补全 |
| `Ctrl + C` | 终止当前前台进程 |
| `Ctrl + Z` | 挂起当前进程（可用 `fg` 恢复） |
| `Ctrl + D` | 退出当前 Shell（EOF） |
| `Ctrl + L` | 清屏（等价于 `clear`） |
| `Ctrl + A` / `Ctrl + E` | 光标跳到行首 / 行尾 |
| `Ctrl + U` / `Ctrl + K` | 删除光标前 / 光标后内容 |
| `Ctrl + R` | 反向搜索历史命令 |
| `↑` / `↓` | 浏览历史命令 |
| `Ctrl + W` | 删除光标前一个单词 |

### 2.3 获取帮助

- `man 命令`：查看命令手册，如 `man ls`（`q` 退出，`/` 搜索，`n` 下一个匹配）
- `命令 --help` 或 `命令 -h`：快速查看用法
- `info 命令`：更详细的文档
- `whatis 命令`：一句话说明命令用途
- `apropos 关键词`：按功能关键词搜索命令

```bash
man ls
ls --help
whatis grep
apropos compress
```

### 2.4 重定向与管道

```bash
# 重定向
command > file      # 标准输出覆盖写入文件
command >> file     # 标准输出追加到文件
command < file      # 从文件读取标准输入
command 2> err.log  # 标准错误单独写入文件
command > out.log 2>&1   # 标准输出和错误都写入同一文件
command > /dev/null      # 丢弃输出（/dev/null 是黑洞设备）

# 管道：把前一个命令的输出作为后一个命令的输入
ps aux | grep wrf
ls | wc -l
cat file | head -20
```

**注意**：`2>&1` 表示把文件描述符 2（stderr）重定向到 1（stdout）当前指向的位置，必须写成 `2>&1` 而不是 `2>1`。

---

## 3. 文件与目录操作

### 3.1 目录操作

```bash
pwd                       # 显示当前工作目录
cd /home/user             # 切换目录
cd ~  或 cd               # 回到家目录
cd -                      # 回到上次目录
cd ..                     # 上一级
mkdir dir1                # 创建目录
mkdir -p a/b/c            # 递归创建多级目录
rmdir dir                 # 删除空目录（非空会报错）
ls                        # 列出文件
ls -l                     # 长格式（权限、属主、大小、时间）
ls -a                     # 显示隐藏文件（以 . 开头）
ls -lh                    # 人类可读大小（K/M/G）
ls -lt                    # 按修改时间排序
ls -lR                    # 递归列出
```

### 3.2 文件操作

```bash
touch file.txt            # 创建空文件 / 更新文件时间戳
cp file1 file2            # 复制文件
cp -r dir1 dir2           # 递归复制目录
cp -i file1 file2         # 覆盖前提示
mv file1 file2            # 移动 / 重命名
rm file                   # 删除文件
rm -r dir                 # 递归删除目录
rm -f file                # 强制删除不提示
rm -rf dir                # 慎用！强制递归删除
```

> ⚠️ `rm -rf` 具有破坏性，执行前务必确认路径正确，尤其是 `rm -rf /` 或 `rm -rf ~` 会造成灾难性后果。删除重要数据前建议先备份。

### 3.3 链接（ln）

- **软链接（符号链接）**：类似 Windows 快捷方式，可跨文件系统，可指向目录；源文件删除后失效
- **硬链接**：多个名字指向同一 inode，不可跨文件系统，不可指向目录；删除其中一个不影响另一个

```bash
ln -s /data/file.txt link.txt   # 创建软链接
ln /data/file.txt hard.txt      # 创建硬链接
ls -li                          # 查看 inode 编号
readlink link.txt               # 查看软链接指向
```

### 3.4 文件类型与元信息

```bash
file test.nc               # 查看文件类型
stat test.nc               # 查看详细元信息（大小、权限、时间戳、inode）
```

---

## 4. 文本查看与处理

### 4.1 查看文件

```bash
cat file            # 输出全部内容
cat -n file         # 带行号输出
less file           # 分页查看（推荐大文件）：空格翻页、/搜索、q退出
more file           # 分页查看（功能较少）
head -20 file       # 查看前 20 行（默认 10 行）
tail -20 file       # 查看后 20 行
tail -f file        # 实时跟踪文件新增内容（看日志必备，Ctrl+C 退出）
tail -n 50 -f log.txt
nl file             # 带行号输出
```

### 4.2 文本统计与处理

```bash
wc file             # 行数、单词数、字节数
wc -l file          # 只统计行数
sort file           # 排序（默认按字典序）
sort -n file        # 按数值排序
sort -r file        # 降序
sort -k2 file       # 按第 2 列排序
uniq                # 去重（必须先 sort，只去相邻重复）
sort file | uniq -c # 统计每行出现次数
cut -d: -f1 /etc/passwd      # 按冒号分隔取第 1 列
cut -c1-10 file              # 取每行前 10 个字符
paste a.txt b.txt            # 按列合并文件
tr 'a-z' 'A-Z' < file        # 大小写转换
diff file1 file2             # 比较文件差异
cmp file1 file2              # 逐字节比较
```

### 4.3 编码与十六进制

```bash
file -i file.txt       # 查看文件编码
iconv -f gbk -t utf8 old.txt > new.txt   # 编码转换（处理中文乱码常用）
od -c file             # 八进制/字符方式查看
xxd file               # 十六进制查看
```

---

## 5. 文件查找

### 5.1 find（最强大、最常用）

```bash
find . -name "*.nc"            # 按文件名查找（当前目录递归）
find /data -name "wrfout*"     # 指定路径查找
find . -type f                 # 只找普通文件
find . -type d                 # 只找目录
find . -size +100M             # 大于 100MB 的文件
find . -size -1k               # 小于 1KB
find . -mtime -7               # 最近 7 天内修改
find . -mtime +30              # 30 天前修改
find . -name "*.log" -exec rm {} \;    # 找到后执行删除
find . -name "*.tmp" -delete           # 直接删除
find . -maxdepth 2 -name "*.nc"        # 限制搜索深度
find . -perm 755               # 按权限查找
find . -user username          # 按属主查找
find . -newer ref.txt          # 比 ref.txt 更新的文件
```

### 5.2 其他查找命令

```bash
locate wrfout        # 基于数据库快速查找（需 updatedb 更新，可能不含最新文件）
which mpirun         # 查找命令所在路径
whereis gcc          # 查找命令、源码、man 手册位置
type ls              # 显示命令类型（内置/别名/外部命令）
```

### 5.3 在文件内容中查找

```bash
grep "keyword" file          # 在文件中匹配
grep -r "keyword" /path/     # 递归搜索目录
grep -n "error" log.txt      # 显示行号
grep -i "warning" file       # 忽略大小写
grep -v "^#" config          # 排除注释行
grep -c "error" log          # 统计匹配行数
grep -l "keyword" *.txt      # 只显示包含关键字的文件名
grep -A2 -B2 "error" log     # 显示匹配行及前后各 2 行
```

---

## 6. 文件压缩与归档

### 6.1 tar（最常用）

```bash
# 打包压缩
tar -czvf archive.tar.gz dir/       # 打包并用 gzip 压缩
tar -cjvf archive.tar.bz2 dir/      # 用 bzip2 压缩（更小更慢）
tar -cJvf archive.tar.xz dir/       # 用 xz 压缩
tar -czvf archive.tar.gz --exclude="*.log" dir/   # 排除某些文件

# 解压
tar -xzvf archive.tar.gz            # 解压到当前目录
tar -xzvf archive.tar.gz -C /target # 解压到指定目录
tar -tzvf archive.tar.gz            # 只查看内容不解压
tar -xvf archive.tar                # 解压未压缩的 tar
```

### 6.2 单独压缩工具

```bash
gzip file            # 压缩为 file.gz（原文件删除）
gzip -d file.gz      # 解压
gunzip file.gz
bzip2 file           # bzip2 压缩
xz file              # xz 压缩
zip -r archive.zip dir/    # 压缩为 zip
unzip archive.zip          # 解压 zip
unzip -l archive.zip       # 查看 zip 内容
```

### 6.3 直接查看压缩文件内容

```bash
zcat file.gz         # 查看 gz 文件内容
zgrep "error" file.gz
zless file.gz
```

> 科研中最常见的组合是 `tar -xzvf` 解压源码包，以及 `tar -czvf` 打包结果数据。建议统一使用 `.tar.gz`。

---

## 7. 用户与权限管理

### 7.1 用户与用户组概念

- 用户信息：`/etc/passwd`；组信息：`/etc/group`；密码（加密）：`/etc/shadow`
- 每个用户有 UID（用户 ID），root 的 UID 为 0
- 每个文件有属主（owner）、属组（group）、其他用户（others）

### 7.2 查看用户与身份

```bash
whoami          # 当前用户名
id              # 当前用户 UID、GID、所属组
id username     # 查看指定用户
who             # 当前登录用户
w               # 登录用户及其操作
last            # 最近登录记录
groups          # 当前用户所属组
```

### 7.3 用户管理（需 root 或 sudo）

```bash
sudo useradd -m -s /bin/bash zhangsan     # 创建用户并建家目录、指定 Shell
sudo passwd zhangsan                      # 设置/修改密码
sudo userdel -r zhangsan                  # 删除用户并删除家目录
sudo usermod -aG sudo zhangsan            # 把用户加入 sudo 组（-aG 追加）
sudo usermod -s /bin/zsh zhangsan         # 修改用户默认 Shell
sudo groupadd team1                       # 创建组
sudo groupdel team1                       # 删除组
```

### 7.4 权限基础

`ls -l` 输出中权限字段共 10 位，例如 `-rwxr-xr--`：
- 第 1 位：文件类型（`-` 普通文件、`d` 目录、`l` 链接、`b/c` 设备）
- 第 2-4 位：属主权限（r 读、w 写、x 执行）
- 第 5-7 位：属组权限
- 第 8-10 位：其他用户权限

权限数值（二进制加权）：读 r=4，写 w=2，执行 x=1

| 数值 | 含义 |
|---|---|
| 7 | rwx（读+写+执行） |
| 6 | rw-（读+写） |
| 5 | r-x（读+执行） |
| 4 | r--（只读） |
| 0 | ---（无权限） |

### 7.5 chmod（修改权限）

```bash
chmod 755 script.sh     # rwxr-xr-x，属主可读写执行，其他人可读执行
chmod 644 file.txt      # rw-r--r--，常见于普通数据文件
chmod 600 id_rsa        # rw-------，私钥文件必须这样
chmod +x script.sh      # 给所有用户加执行权限
chmod u+x file          # 仅属主加执行权限
chmod g-w file          # 去掉组写权限
chmod -R 755 dir/       # 递归修改目录下所有文件
```

### 7.6 chown / chgrp（修改属主属组）

```bash
sudo chown user file                # 修改属主
sudo chown user:group file          # 同时修改属主和属组
sudo chown -R user:group dir/       # 递归修改
sudo chgrp group file               # 只修改属组
```

### 7.7 特殊权限

- **setuid (4xxx)**：执行时以文件属主身份运行（如 `/usr/bin/passwd`）
- **setgid (2xxx)**：目录内新建文件继承目录属组
- **sticky (1xxx)**：目录内只能删除自己创建的文件（如 `/tmp`，权限为 `drwxrwxrwt`）

```bash
chmod u+s /path/file     # 加 setuid
chmod 1777 /tmp          # rwxrwxrwt，sticky 位
```

### 7.8 默认权限 umask

```bash
umask            # 查看当前 umask（如 0022）
umask 022        # 修改默认权限掩码
```

### 7.9 su 与 sudo

```bash
su -                  # 切换到 root（- 表示同时加载 root 环境）
su - username         # 切换到指定用户
sudo command          # 以 root 权限执行单条命令
sudo -i               # 进入 root 交互 Shell
sudo -u user command  # 以指定用户身份执行
```

`sudo` 权限由 `/etc/sudoers` 控制（用 `visudo` 编辑）。sudo 执行需要密码，密码有缓存时间（默认 15 分钟）。

---

## 8. 环境变量与 Shell 配置

### 8.1 环境变量

```bash
echo $PATH               # 查看 PATH
printenv                 # 打印所有环境变量
env                      # 同上
export MYVAR=value       # 定义并导出环境变量（子进程可见）
MYVAR=value              # 仅当前 Shell 生效的变量
unset MYVAR              # 删除变量
```

常用环境变量：
- `PATH`：可执行文件搜索路径（冒号分隔）
- `HOME`：当前用户家目录
- `SHELL`：当前 Shell
- `LANG`：语言环境（如 `zh_CN.UTF-8`）
- `LD_LIBRARY_PATH`：动态库搜索路径（源码编译软件常需设置）
- `NETCDF`、`HDF5`、`MPICH`：科学计算软件自定义变量（WRF 安装关键）

### 8.2 修改 PATH

```bash
# 临时生效（当前终端）
export PATH=$PATH:/opt/software/bin

# 永久生效：写入 ~/.bashrc
echo 'export PATH=$PATH:/opt/software/bin' >> ~/.bashrc
source ~/.bashrc
```

### 8.3 Shell 配置文件加载顺序

登录式 Shell（ssh 登录）：`/etc/profile` → `~/.profile`（或 `~/.bash_profile`）→ `~/.bashrc`
非登录式 Shell（新终端）：`~/.bashrc`

```bash
source ~/.bashrc      # 立即重新加载配置（等价于 . ~/.bashrc）
```

### 8.4 常用配置示例（~/.bashrc）

```bash
# 别名
alias ll='ls -alF'
alias la='ls -A'
alias rm='rm -i'
alias q='exit'

# 提示符
export PS1='\u@\h:\w\$ '

# WRF 相关环境变量（示例）
export DIR=/home/user/Build_WRF
export PATH=$DIR/netcdf/bin:$PATH
export NETCDF=$DIR/netcdf
```

### 8.5 命令历史

```bash
history          # 查看历史命令
history 20       # 查看最近 20 条
!ls              # 重新执行最近以 ls 开头的命令
!!               # 重新执行上一条命令
!$               # 上一条命令的最后一个参数
```

### 8.6 通配符

```bash
ls *.nc          # 匹配任意多个字符
ls file?.txt     # ？匹配单个字符
ls [abc]*.txt    # 匹配 a/b/c 开头
ls file[1-3].txt # 匹配数字 1-3
ls {1..10}.txt   # 花括号展开（Bash）
```

### 8.7 命令替换与变量替换

```bash
echo "Today is $(date)"        # $( ) 命令替换
echo "Today is `date`"         # 反引号命令替换（旧写法）
echo $HOME                     # 变量引用
echo ${HOME}                   # 变量引用（推荐写法）
```

---

## 9. 网络与远程连接

### 9.1 网络信息查看

```bash
ip addr              # 查看 IP 地址（推荐）
ip route             # 查看路由
hostname             # 查看主机名
hostname -I          # 查看本机 IP
ss -tulnp            # 查看监听端口（推荐，替代 netstat）
netstat -tulnp       # 旧命令，需安装 net-tools
ping www.baidu.com   # 测试连通性
traceroute host      # 路由追踪
nslookup domain      # DNS 查询
dig domain           # DNS 查询（更详细）
curl -I https://xxx  # 查看 HTTP 响应头
```

### 9.2 SSH 远程登录

```bash
# 基本登录
ssh user@192.168.1.100
ssh -p 2222 user@host        # 指定端口
ssh -X user@host             # 开启 X11 图形转发

# 密钥登录（免密）
ssh-keygen -t ed25519        # 生成密钥（可指定 -f ~/.ssh/id_ed25519）
ssh-copy-id user@host        # 把公钥复制到远程主机
ssh user@host                # 之后即可免密登录

# 配置文件 ~/.ssh/config（可定义主机别名）
Host cluster
    HostName 192.168.1.100
    User zhangsan
    Port 22
# 之后直接 ssh cluster
```

### 9.3 文件传输

```bash
# scp（加密拷贝）
scp file.txt user@host:/home/user/
scp -r dir user@host:/home/user/    # 递归拷贝目录
scp user@host:/path/file.txt ./     # 从远程下载

# rsync（增量同步，科研拷贝大目录首选）
rsync -avz /local/dir/ user@host:/remote/dir/
rsync -avz --delete src/ dst/       # 删除源端已不存在的文件（双向一致）
rsync -avz --progress data/ bak/    # 显示进度
rsync -e 'ssh -p 2222' src user@host:dst   # 指定端口

# sftp 交互式传输
sftp user@host
# 内部命令：get file 下载；put file 上传；ls；cd
```

### 9.4 下载工具

```bash
wget -c https://url/file.tar.gz     # 下载，-c 断点续传
wget -O name.tar.gz https://url     # 指定保存文件名
curl -O https://url/file.tar.gz     # 下载并保留原名
curl -o file https://url            # 指定文件名
curl -X POST -d "data" http://...   # 发送 POST 请求
```

### 9.5 长时间任务后台运行

```bash
nohup command > log.txt 2>&1 &      # 退出终端后仍继续运行
nohup python run.py > out.log 2>&1 &

# tmux（终端复用器，推荐，可断开重连）
tmux new -s work        # 新建会话
tmux detach             # 断开（Ctrl+B 然后 D）
tmux attach -t work     # 重新连接
tmux ls                 # 列出会话

# screen（另一种复用器）
screen -S work          # 新建
screen -r work          # 恢复
```

> 在远程服务器跑 WRF 等长时间任务，务必使用 `nohup` 或 `tmux`/`screen`，避免 SSH 断开导致任务中断。


---

# 第二部分 系统管理与软件安装

## 10. 进程管理与系统监控

### 10.1 查看进程

```bash
ps aux              # 查看所有进程（BSD 风格）
ps -ef              # 查看所有进程（System V 风格）
ps -ef | grep wrf   # 过滤查看特定进程
pstree              # 以树状查看进程关系
pidof sshd          # 查看某程序 PID
pgrep -l python     # 按名字查 PID
```

`ps aux` 关键列：USER（用户）、PID（进程号）、%CPU、%MEM、VSZ/RSS（内存）、STAT（状态）、START、TIME、COMMAND

STAT 常见状态：`R` 运行、`S` 睡眠、`D` 不可中断睡眠、`Z` 僵尸进程、`T` 停止、`<` 高优先级、`N` 低优先级

### 10.2 动态监控

```bash
top                 # 动态监控（P 按 CPU 排序、M 按内存排序、q 退出）
htop                # 更友好的监控（需安装：sudo apt install htop）
free -h             # 查看内存使用
uptime              # 系统运行时间与负载
watch -n 2 free -h  # 每 2 秒刷新
vmstat 1 5          # 每秒输出一次，共 5 次（CPU/内存/IO）
iostat              # 磁盘 IO 监控
```

### 10.3 终止进程

```bash
kill PID            # 发送 TERM 信号（优雅终止）
kill -9 PID         # 强制终止（SIGKILL，无法被忽略）
kill -15 PID        # 默认 TERM
pkill python        # 按进程名终止
killall mpirun      # 按名称终止所有匹配进程
```

> `kill -9` 是最后手段，可能导致数据丢失；先尝试 `kill`（TERM），无效再 `-9`。

### 10.4 后台任务管理

```bash
command &           # 后台运行
jobs                # 查看后台任务
fg %1               # 将后台任务 1 调到前台
bg %1               # 将挂起任务放后台继续运行
Ctrl+Z              # 挂起当前任务
```

### 10.5 进程优先级

```bash
nice -n -5 command      # 以更高优先级运行（nice 范围 -20~19，默认 0）
renice -n -5 PID        # 修改运行中进程优先级
```

### 10.6 文件占用排查

```bash
lsof -i :8080       # 查看占用 8080 端口的进程
lsof file.txt       # 查看打开某文件的进程
lsof | grep deleted # 查看被删除但仍被占用的文件（磁盘空间不释放的常见原因）
```

### 10.7 日志与内核信息

```bash
dmesg               # 内核日志（硬件、驱动问题）
dmesg | tail -50    # 看最近的内核日志
journalctl          # systemd 日志
journalctl -u sshd -f   # 跟踪某服务日志
```

---

## 11. 系统信息与硬件

```bash
uname -a                 # 内核版本与系统架构
cat /etc/os-release      # 发行版信息
cat /etc/lsb-release     # Ubuntu 版本
lscpu                    # CPU 详细信息（核心数、线程数、架构、频率）
free -h                  # 内存总量与使用
lsblk                    # 磁盘与分区
df -h                    # 文件系统使用情况
du -sh /path             # 目录占用空间
hostnamectl              # 主机名与系统信息
uptime                   # 开机时长与负载
nproc                    # CPU 逻辑核心数（并行计算常用）
lsusb                    # USB 设备
lspci                    # PCI 设备（如显卡）
```

---

## 12. 磁盘与文件系统

### 12.1 磁盘使用情况

```bash
df -h               # 各挂载点磁盘占用（人类可读）
df -i               # inode 使用情况（inode 满但空间有余的排查）
du -sh dir/         # 目录总大小
du -sh *            # 当前目录下各项大小
du -h --max-depth=1 /home   # 限制深度
```

**排查"磁盘满了"的标准流程**：
```bash
df -h                       # 先看哪个分区满了
du -sh /* 2>/dev/null       # 逐层定位大目录
du -h --max-depth=1 /home/user 2>/dev/null | sort -hr | head
find / -xdev -size +1G -type f 2>/dev/null   # 找超大文件
```

### 12.2 挂载与卸载

```bash
mount                       # 查看当前挂载
mount /dev/sdb1 /mnt/data   # 挂载分区（需 sudo）
umount /mnt/data            # 卸载
lsblk -f                    # 查看分区格式与 UUID
blkid                       # 查看块设备 UUID
```

### 12.3 分区与格式化（了解，慎用）

```bash
sudo fdisk -l           # 查看磁盘与分区表
sudo fdisk /dev/sdb     # 交互式分区（危险操作）
sudo mkfs.ext4 /dev/sdb1   # 格式化为 ext4（会清空数据！）
```

### 12.4 /etc/fstab（开机自动挂载）

格式：`设备 UUID  挂载点  文件系统类型  选项  备份  检查顺序`
```bash
# 示例行
UUID=xxxx-xxxx  /data  ext4  defaults  0  2
```
修改后 `sudo mount -a` 生效（不要随意改动，写错可能导致无法开机）。

---

## 13. 服务管理与定时任务

### 13.1 systemd（现代 Ubuntu 服务管理）

```bash
systemctl status sshd        # 查看服务状态（Ubuntu 上 SSH 服务名为 ssh）
systemctl start ssh
systemctl stop ssh
systemctl restart ssh
systemctl enable ssh         # 开机自启
systemctl disable ssh        # 取消开机自启
systemctl list-units --type=service --state=running   # 列出运行中的服务
systemctl daemon-reload      # 重载配置（修改 unit 文件后）
systemd-analyze              # 分析开机耗时
```

> 注意：Ubuntu 上 SSH 服务的单元名为 `ssh`（不是 `sshd`），但 RHEL/CentOS 为 `sshd`。

### 13.2 journalctl 查看日志

```bash
journalctl -u ssh -n 50      # 查看 ssh 服务最近 50 行日志
journalctl -u ssh -f         # 实时跟踪
journalctl --since "1 hour ago"
```

### 13.3 crontab 定时任务

```bash
crontab -l          # 查看当前用户的定时任务
crontab -e          # 编辑定时任务
crontab -r          # 删除所有定时任务
```

cron 格式：`分 时 日 月 周 命令`
```bash
# 每分钟执行
* * * * * command
# 每天凌晨 2 点执行
0 2 * * * /home/user/backup.sh
# 每小时的 5 分执行
5 * * * * command
# 每周一 8 点执行
0 8 * * 1 command
# 每 10 分钟
*/10 * * * * command
```

示例：每天凌晨 3 点备份数据
```bash
0 3 * * * tar -czf /backup/data_$(date +\%Y\%m\%d).tar.gz /data
```
> 注意：cron 命令中 `%` 需要转义为 `\%`。

### 13.4 at 一次性任务

```bash
at now + 1 hour          # 一小时后执行（然后输入命令，Ctrl+D 结束）
at 22:00                 # 晚上 10 点执行
atq                      # 查看待执行任务
```

---

## 14. 软件安装

### 14.1 apt（Debian/Ubuntu 包管理器）

```bash
sudo apt update                  # 更新软件源索引（必须定期执行）
sudo apt upgrade                 # 升级所有已安装软件
sudo apt install <包名>          # 安装软件
sudo apt install vim htop git    # 一次安装多个
sudo apt remove <包名>           # 卸载（保留配置文件）
sudo apt purge <包名>            # 彻底卸载（含配置）
sudo apt autoremove              # 自动清理无用的依赖包
sudo apt search <关键词>         # 搜索软件
apt show <包名>                  # 查看软件详情
apt list --installed             # 列出已安装软件
sudo apt clean                   # 清理下载缓存
```

**换国内源（加速）**：编辑 `/etc/apt/sources.list`（Ubuntu 22.04 及以后可能是 `.sources` 文件），将 `archive.ubuntu.com` 替换为清华/阿里/中科大镜像，然后 `sudo apt update`。

### 14.2 dpkg（底层包工具）

```bash
dpkg -l                # 列出所有已安装包
dpkg -L <包名>         # 查看包安装了哪些文件
dpkg -i package.deb    # 安装本地 deb 包（需 sudo）
dpkg -r <包名>         # 卸载
```

### 14.3 源码编译安装（科研软件最常见方式）

标准三步流程：
```bash
./configure --prefix=/opt/mylib
make
make install
```

常用编译参数与工具：
```bash
./configure --help                      # 查看所有配置选项
./configure --prefix=$HOME/install      # 指定安装目录
make -j4                                # 4 核并行编译（加速）
make check                              # 运行测试
make install                            # 安装
make clean                              # 清理编译中间文件
```

**源码编译需安装编译工具链**：
```bash
sudo apt install build-essential        # 含 gcc、g++、make 等
sudo apt install gfortran               # Fortran 编译器（WRF 必需）
```

**常见编译错误排查思路**：
- 缺少头文件 → 安装 `*-dev` 包
- 找不到库 → 检查 `LD_LIBRARY_PATH`、`LDFLAGS`
- 找不到编译器 → 检查 PATH 与 `CC`/`FC` 环境变量

### 14.4 conda / Miniconda（Python 科学环境管理）

安装 Miniconda：
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# 安装后重启终端或 source ~/.bashrc
```

常用命令：
```bash
conda create -n myenv python=3.10     # 创建环境（指定 Python 版本）
conda activate myenv                  # 激活环境
conda deactivate                      # 退出环境
conda env list                        # 查看所有环境
conda install numpy pandas            # 安装包
conda search numpy                    # 搜索包
conda list                            # 列出当前环境已装包
conda remove -n myenv --all           # 删除环境
conda env export > env.yml            # 导出环境配置
conda env create -f env.yml           # 从配置恢复环境
```

**加速：配置国内 conda 源（清华镜像）**
```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --set show_channel_urls yes
```

> 科研建议：用 conda 创建独立环境管理 WRF 后处理工具（wrf-python、xarray、cartopy 等），避免污染系统 Python。

### 14.5 pip（Python 包管理）

```bash
pip install numpy                 # 安装
pip install -r requirements.txt   # 按文件批量安装
pip list                          # 列出已安装
pip show numpy                    # 查看包信息
pip uninstall numpy               # 卸载
pip freeze > requirements.txt     # 导出当前环境依赖
pip install --upgrade pip         # 升级 pip
```

**配置国内 pip 源（清华镜像）**：
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**venv 虚拟环境（系统自带 Python 用）**：
```bash
python3 -m venv myenv
source myenv/bin/activate
deactivate
```

### 14.6 其他安装方式

```bash
sudo snap install <软件>          # snap 包（Ubuntu 自带）
sudo apt install flatpak          # flatpak（较少用）
```

---

# 第三部分 文本处理与脚本编程

## 15. grep / sed / awk 与正则表达式

### 15.1 正则表达式基础

| 符号 | 含义 | 示例 |
|---|---|---|
| `.` | 任意单个字符 | `a.c` 匹配 abc、axc |
| `*` | 前一个字符重复 0 次或多次 | `ab*c` 匹配 ac、abc、abbc |
| `+` | 前一个字符重复 1 次或多次（需 -E） | `ab+c` |
| `?` | 前一个字符出现 0 或 1 次（需 -E） | `ab?c` |
| `[]` | 字符集合 | `[abc]`、`[0-9]`、`[a-z]` |
| `[^]` | 排除集合 | `[^0-9]` 非数字 |
| `^` | 行首 | `^#` 注释行 |
| `$` | 行尾 | `end$` |
| `()` | 分组 | `(ab)+` |
| `\|` | 或（需 -E） | `cat\|dog` |
| `{}` | 重复次数（需 -E） | `a{2,4}` |
| `\b` | 单词边界 | `\bwrf\b` |
| `\d`、`\w`、`\s` | 数字、单词字符、空白 | |

### 15.2 grep（文本搜索）

```bash
grep "error" file                 # 基础匹配
grep -E "error|fail" log          # 扩展正则（或）
grep -E "^[0-9]+" file            # 行首数字
grep -P "\d+" file                # Perl 正则（\d）
grep -v "^#" config               # 排除注释行
grep -n "wrf" namelist.input      # 带行号
grep -r "SUCCESS" .               # 递归
grep -i "warning" log             # 忽略大小写
grep -w "file" txt                # 全词匹配
```

**实用场景**：
```bash
# 查看 WRF 运行日志中的成功标志
grep "SUCCESS" rsl.out.0000
# 统计错误次数
grep -c "ERROR" rsl.error.0000
# 找出包含 error 的文件
grep -rl "error" /home/user/logs/
```

### 15.3 sed（流编辑器）

基本格式：`sed [选项] '脚本' 文件`

```bash
sed 's/old/new/' file            # 每行第一个 old 替换为 new
sed 's/old/new/g' file           # 全部替换（g 全局）
sed -i 's/foo/bar/g' file        # 直接修改原文件（-i）
sed -n '5,10p' file              # 打印第 5-10 行
sed -n '1p' file                 # 打印第一行
sed '/^$/d' file                 # 删除空行（d 删除）
sed '/pattern/d' file            # 删除匹配行
sed -i '/^#/d' config            # 删除注释行
sed 's/^/>> /' file              # 每行行首加前缀
sed 's/$/<< /' file              # 行尾追加
sed 's/pattern/& &/' file        # & 代表匹配到的内容
```

**实用场景**：
```bash
# 备份后替换（保留原文件）
sed -i.bak 's/old/new/g' file
# 在 namelist 中批量替换路径
sed -i 's|/home/old|/home/new|g' namelist.wps
```

### 15.4 awk（文本处理神器）

基本格式：`awk [选项] '模式 {动作}' 文件`

```bash
awk '{print $1}' file            # 打印第一列（默认按空白分隔）
awk '{print $1, $3}' file        # 打印第一、三列
awk -F: '{print $1}' /etc/passwd # 指定分隔符为冒号
awk '{print NR, $0}' file        # NR 行号，$0 整行
awk '{sum += $1} END {print sum}' data   # 求第一列总和
awk '$3 > 100 {print $1}' data   # 条件过滤
awk 'NR>=2 && NR<=5 {print}' file # 打印 2-5 行
awk '{printf "%s %.2f\n", $1, $2}' file  # 格式化输出
awk 'BEGIN {print "start"} {print} END {print "end"}' file
awk '/pattern/ {print}' file     # 匹配正则的行
awk '{a[$1]++} END {for (k in a) print k, a[k]}' file   # 按第一列统计计数
```

awk 内置变量：`NR` 当前行号、`NF` 当前行字段数、`$0` 整行、`$1`~`$n` 各字段、`FS` 字段分隔符、`OFS` 输出分隔符

**实用场景**：
```bash
# 提取日志中的时间与温度
awk '{print $1, $2, $7}' obs.log
# 计算文件大小总和
ls -l *.nc | awk '{sum += $5} END {print sum/1024/1024 " MB"}'
# 统计各状态出现次数
ps aux | awk '{print $8}' | sort | uniq -c
```

---

## 16. Vim 编辑器

### 16.1 三种模式

- **普通模式**：默认模式，用于移动与操作
- **插入模式**：输入文字（按 `i` 进入）
- **命令模式**：输入命令（按 `:` 进入）

```bash
vim file.txt        # 打开/创建文件
vim +20 file.txt    # 打开并跳到第 20 行
```

### 16.2 基本操作速查

| 操作 | 按键 |
|---|---|
| 进入插入模式 | `i`（光标前）、`a`（光标后）、`o`（下一行新建）、`O`（上一行新建） |
| 退出插入模式 | `Esc` |
| 保存 | `:w` |
| 退出 | `:q`；强制退出 `:q!` |
| 保存并退出 | `:wq` 或 `ZZ` |
| 移动光标 | `h` `j` `k` `l`（左 下 上 右） |
| 跳行首/行尾 | `0` / `$` |
| 跳文件首/尾 | `gg` / `G` |
| 跳第 N 行 | `:N` 或 `N G` |
| 删除当前字符 | `x` |
| 删除当前行 | `dd` |
| 删除 N 行 | `N dd` |
| 复制当前行 | `yy` |
| 粘贴 | `p`（光标后）、`P`（光标前） |
| 撤销 | `u`；重做 `Ctrl+R` |
| 查找 | `/keyword`（`n` 下一个、`N` 上一个） |
| 替换 | `:s/old/new/g`（当前行）；`:%s/old/new/g`（全文） |
| 显示行号 | `:set nu`；取消 `:set nonu` |
| 分屏 | `:sp` 水平、`:vsp` 垂直，`Ctrl+W` 切换 |
| 保存为其他文件 | `:w newfile` |
| 打开多个文件 | `vim f1 f2`，`:n` 下一个，`:prev` 上一个 |

### 16.3 vim 个性化配置（~/.vimrc）

```vim
set nu              " 显示行号
set tabstop=4       " Tab 宽度
set shiftwidth=4    " 缩进宽度
set expandtab       " 用空格代替 Tab
set hlsearch        " 高亮搜索
set incsearch       " 增量搜索
syntax on           " 语法高亮
set mouse=a         " 启用鼠标
```

> 修改 WRF 的 namelist.wps、namelist.input 等配置文件，vim 是最常用工具。

---

## 17. Shell 脚本编程

### 17.1 脚本基础

```bash
#!/bin/bash
# 这是注释
echo "Hello World"
```

执行方式：
```bash
bash script.sh        # 用 bash 解释执行（无需执行权限）
./script.sh           # 直接执行（需 chmod +x）
source script.sh      # 在当前 Shell 执行（变量会保留）
```

### 17.2 变量

```bash
name="wrf"                # 赋值（等号两边不能有空格）
echo $name                # 引用
echo "${name}_run"        # 变量边界
readonly pi=3.14          # 只读变量
unset name                # 删除变量

# 位置参数
# 脚本 $0=脚本名，$1-$9 第 1-9 个参数，$# 参数个数，$@/$* 所有参数，$? 上条命令退出码
echo "脚本名: $0, 第一个参数: $1, 参数个数: $#"
```

### 17.3 数组

```bash
arr=(a b c)
echo ${arr[0]}           # a
echo ${arr[@]}           # 所有元素
echo ${#arr[@]}          # 元素个数
for i in "${arr[@]}"; do echo $i; done
```

### 17.4 运算

```bash
echo $((3 + 5))          # 整数运算
echo $((10 / 3))
# 浮点运算用 bc
echo "scale=2; 10/3" | bc
```

### 17.5 条件判断

```bash
if [ -f file ]; then
    echo "文件存在"
elif [ -d dir ]; then
    echo "是目录"
else
    echo "不存在"
fi
```

常用测试：
```bash
[ -f file ]    # 文件存在且为普通文件
[ -d dir ]     # 是目录
[ -e path ]    # 路径存在
[ -z "$var" ]  # 变量为空
[ -n "$var" ]  # 变量非空
[ "$a" = "$b" ]    # 字符串相等（注意 = 两边空格）
[ "$a" != "$b" ]
[ "$n" -gt 10 ]    # 数字比较：-eq -ne -gt -lt -ge -le
[ -x file ]    # 可执行
[ -r file ]    # 可读
```

### 17.6 循环

```bash
# for 数字循环
for i in {1..10}; do
    echo $i
done

# for 文件循环
for f in *.nc; do
    echo "处理 $f"
done

# while 循环
i=1
while [ $i -le 10 ]; do
    echo $i
    i=$((i+1))
done

# 读取文件每行
while read line; do
    echo "$line"
done < file.txt

# break 跳出，continue 跳过本次
```

### 17.7 case 分支

```bash
case "$1" in
    start) echo "启动" ;;
    stop)  echo "停止" ;;
    *)     echo "用法: $0 {start|stop}" ;;
esac
```

### 17.8 函数

```bash
function myfunc() {
    echo "参数: $1 $2"
    return 0
}
myfunc hello world
```

### 17.9 实用脚本示例

**示例 1：批量重命名 .nc 文件（加前缀）**
```bash
#!/bin/bash
for f in *.nc; do
    mv "$f" "wrf_$f"
done
```

**示例 2：备份脚本**
```bash
#!/bin/bash
backup_dir="/backup"
data_dir="/data/wrfout"
date_str=$(date +%Y%m%d_%H%M%S)
mkdir -p $backup_dir
tar -czf "$backup_dir/wrf_$date_str.tar.gz" "$data_dir"
echo "备份完成: $backup_dir/wrf_$date_str.tar.gz"
```

**示例 3：批量提交作业（配合 sbatch）**
```bash
#!/bin/bash
for case in {2019,2020,2021}; do
    sed "s/CASE/$case/g" template.slurm > run_$case.slurm
    sbatch run_$case.slurm
done
```

### 17.10 脚本调试

```bash
bash -x script.sh       # 跟踪执行过程（打印每条命令）
bash -n script.sh       # 只检查语法
# 脚本内开启
set -e      # 任何命令出错即退出
set -u      # 使用未定义变量报错
set -x      # 打印执行过程
```

### 17.11 后台与等待

```bash
#!/bin/bash
./task1.sh &
./task2.sh &
wait                  # 等待所有后台任务完成
echo "全部完成"
```


---

# 第四部分 并行计算与科学计算

## 18. 高性能计算基础

### 18.1 为什么要并行

数值模式（WRF 等）计算量大，单核无法满足时效要求。并行方式：

- **共享内存并行（OpenMP / 多线程）**：多核共享内存，线程间通过共享变量通信。适用于单节点。
- **分布式内存并行（MPI / 多进程）**：进程间通过消息传递通信，可跨节点。适用于集群。

WRF 采用 **MPI（分布式内存）为主**，可结合 OpenMP 混合并行（较少用）。

### 18.2 查看计算资源

```bash
nproc                 # 逻辑 CPU 核心数
lscpu                 # CPU 详细架构（核数、线程、频率）
free -h               # 内存
df -h /data           # 数据盘空间
```

### 18.3 编译优化选项

```bash
# gcc / gfortran 常用优化选项
-O2          # 标准优化（默认推荐）
-O3          # 更激进优化
-O0          # 不优化（调试用）
-g           # 生成调试信息
-Wall        # 显示全部警告
-fopenmp     # 启用 OpenMP
-march=native # 针对本机 CPU 指令集优化
-O2 -march=native   # 常用组合
```

---

## 19. OpenMP 共享内存并行

### 19.1 概念

OpenMP 是共享内存并行编程标准，用编译指导指令 `#pragma omp`（C/C++）或 `!$OMP`（Fortran）实现。

### 19.2 示例（C）

```c
#include <stdio.h>
#include <omp.h>

int main() {
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        printf("Hello from thread %d\n", tid);
    }
    return 0;
}
```

### 19.3 编译与运行

```bash
gcc -fopenmp -o hello_omp hello.c
OMP_NUM_THREADS=4 ./hello_omp      # 用 4 个线程运行
export OMP_NUM_THREADS=8           # 或先设置环境变量
./hello_omp
```

### 19.4 常用 OpenMP 指令

```c
#pragma omp parallel for        // 并行 for 循环
#pragma omp parallel num_threads(4)
#pragma omp critical            // 临界区（互斥）
#pragma omp reduction(+:sum)    // 归约
#pragma omp single / master     // 单线程执行
```

### 19.5 环境变量

```bash
OMP_NUM_THREADS        # 线程数
OMP_DYNAMIC            # 是否动态调整线程
OMP_STACKSIZE          # 栈大小
```

---

## 20. MPI 分布式并行

### 20.1 MPI 实现

- **MPICH**：经典实现，WRF 官方教程默认推荐
- **OpenMPI**：另一主流实现

Ubuntu 快速安装：
```bash
sudo apt install mpich libmpich-dev          # MPICH
sudo apt install openmpi-bin libopenmpi-dev   # OpenMPI
```

查看安装：
```bash
mpirun --version
mpif90 --version
which mpirun
```

### 20.2 示例（C，MPI 基础流程）

```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);   // 当前进程号
    MPI_Comm_size(MPI_COMM_WORLD, &size);   // 总进程数
    printf("Hello from rank %d of %d\n", rank, size);
    MPI_Finalize();
    return 0;
}
```

### 20.3 编译与运行

```bash
mpicc -o hello_mpi hello.c          # C 程序用 mpicc
mpif90 -o hello_mpi hello.f90       # Fortran 程序用 mpif90
mpic++ -o hello_mpi hello.cpp       # C++ 用 mpicxx/mpic++

mpirun -np 4 ./hello_mpi            # 4 个进程并行运行
mpiexec -np 4 ./hello_mpi           # 同义命令
mpirun -np 8 ./wrf.exe              # 8 进程运行 WRF
```

### 20.4 多节点运行

```bash
# 主机文件 hostfile（每行一个节点名）
# login01
# compute01
# compute02
mpirun -np 16 -hostfile hostfile ./a.out
mpirun -np 16 --hosts compute01,compute02 ./a.out
```

### 20.5 常见 MPI 函数（了解）

```c
MPI_Init / MPI_Finalize         // 初始化和结束
MPI_Comm_rank / MPI_Comm_size   // 获取进程号和总进程数
MPI_Send / MPI_Recv             // 点对点发送/接收
MPI_Bcast                       // 广播
MPI_Reduce / MPI_Allreduce      // 归约
MPI_Barrier                     // 同步屏障
MPI_Gather / MPI_Scatter        // 收集 / 分发
```

---

## 21. SLURM 作业调度系统

> 大多数超算中心 / 大学 HPC 平台使用 SLURM。登录节点用于编辑提交，计算节点用于跑作业。**不要在登录节点直接运行大规模计算**。

### 21.1 查看资源与队列

```bash
sinfo                     # 查看节点与分区状态
sinfo -Nel                # 详细节点信息
squeue                    # 查看作业队列
squeue -u $USER           # 只看自己的作业
squeue -l                 # 详细格式
```

`sinfo` 中节点状态：`idle` 空闲、`alloc` 已占满、`mix` 部分占用、`down` 故障、`drain` 维护。

### 21.2 提交批处理作业（sbatch）

作业脚本 `job.slurm`：
```bash
#!/bin/bash
#SBATCH --job-name=wrf_run        # 作业名
#SBATCH --partition=compute       # 分区
#SBATCH --nodes=1                 # 节点数
#SBATCH --ntasks=16               # 总进程数
#SBATCH --ntasks-per-node=16      # 每节点进程数
#SBATCH --cpus-per-task=1         # 每进程核数
#SBATCH --time=24:00:00           # 最长运行时间
#SBATCH --output=wrf_%j.out       # 标准输出（%j 为作业号）
#SBATCH --error=wrf_%j.err        # 错误输出
#SBATCH --mail-type=END           # 结束邮件通知
#SBATCH --mail-user=xxx@xx.com

cd $SLURM_SUBMIT_DIR              # 进入提交目录
module load mpich netcdf          # 加载环境（按平台要求）
mpirun -np $SLURM_NTASKS ./wrf.exe
```

提交与查看：
```bash
sbatch job.slurm
squeue -u $USER
scancel <jobid>            # 取消作业
```

### 21.3 交互式作业（srun / salloc）

```bash
srun --partition=compute --nodes=1 --ntasks=4 --time=01:00:00 --pty bash
# 申请资源并进入计算节点交互 Shell

salloc --ntasks=16 --time=2:00:00   # 分配资源后原地交互
mpirun -np 16 ./wrf.exe
```

### 21.4 查看作业详情与历史

```bash
scontrol show job <jobid>      # 查看作业详细信息
sacct -j <jobid>               # 查看作业计费与状态
sacct -u $USER                 # 查看自己的历史作业
sacct --format=JobID,JobName,State,Elapsed,MaxRSS,NodeList
```

### 21.5 SLURM 常用选项汇总

| 选项 | 含义 |
|---|---|
| `--nodes/-N` | 节点数 |
| `--ntasks/-n` | 总进程数 |
| `--ntasks-per-node` | 每节点进程数 |
| `--cpus-per-task/-c` | 每进程 CPU 核数 |
| `--time/-t` | 时间限制（DD-HH:MM:SS 或 HH:MM:SS） |
| `--partition/-p` | 分区（队列） |
| `--mem` | 内存需求 |
| `--gres=gpu:1` | GPU 资源 |
| `--job-name/-J` | 作业名 |
| `--output/--error` | 输出/错误文件 |
| `--array=1-10` | 任务数组（批量并行） |

### 21.6 PBS/Torque 简介（部分平台）

```bash
qsub job.pbs      # 提交
qstat             # 查看
qdel <jobid>      # 删除
```

---

## 22. 环境模块 module

超算平台常用 `module` 管理软件环境，避免冲突。

```bash
module avail            # 查看可用模块
module list             # 查看已加载
module load netcdf      # 加载
module load mpich/4.0.2
module unload netcdf    # 卸载
module purge            # 清空所有
module show netcdf      # 查看模块内容（PATH 等）
```

**为什么用 module**：不同版本软件共存、环境变量自动配置、避免污染系统环境。

---

## 23. 科学计算库与数据工具

### 23.1 编译器

```bash
gcc --version          # C 编译器
g++ --version          # C++ 编译器
gfortran --version     # Fortran 编译器（WRF 必需）
```

### 23.2 netCDF 工具

netCDF 是 WRF 输入输出采用的数据格式。命令行工具：

```bash
# 查看头信息（变量、维度、属性）——最常用
ncdump -h wrfout_d01_2026-09-01_00:00:00

# 查看全部数据
ncdump file.nc

# 查看指定变量
ncdump -v T2 file.nc

# 查看坐标变量
ncdump -c file.nc

# 图形化快速查看（需安装 ncview）
ncview wrfout_d01_2026-09-01_00:00:00
```

安装：
```bash
sudo apt install netcdf-bin ncview
```

### 23.3 NCO（netCDF 操作工具）

```bash
sudo apt install nco

ncks -v T2,T,PSFC in.nc out.nc     # 提取变量子集
ncatted -a units,T2,o,c,K in.nc    # 修改属性
ncra in1.nc in2.nc out.nc          # 时间维求平均
ncecat -u time *.nc out.nc         # 沿新维度拼接
ncbo in1.nc in2.nc diff.nc         # 求差
ncap2 -s "T2C=T2-273.15" in.nc out.nc   # 计算新变量
ncks -d time,0,10 in.nc out.nc     # 截取时间范围
```

### 23.4 CDO（气候数据操作工具）

```bash
sudo apt install cdo

cdo info file.nc                 # 查看变量信息
cdo daymean in.nc out.nc         # 求日平均
cdo monmean in.nc out.nc         # 求月平均
cdo timmean in.nc out.nc         # 求时间平均
cdo remapbil,r360x180 in.nc out.nc  # 重网格插值
cdo selvar,t2m in.nc out.nc      # 选变量
cdo seldate,2026-01-01,2026-01-31 in.nc out.nc   # 选时间段
cdo mergetime f*.nc out.nc       # 时间拼接
```

### 23.5 HDF5 工具

```bash
sudo apt install hdf5-tools
h5ls file.h5          # 列出结构
h5dump file.h5        # 转储内容
```

### 23.6 Python 科学计算栈（WRF 后处理）

常用库：numpy、scipy、pandas、matplotlib、xarray、netCDF4、wrf-python、cartopy、metpy、pyshp

```bash
conda create -n wrf python=3.10
conda activate wrf
conda install numpy scipy matplotlib xarray netcdf4
pip install wrf cartopy metpy
```

```python
# xarray 读取 wrfout 示例
import xarray as xr
ds = xr.open_dataset('wrfout_d01_2026-09-01_00:00:00')
print(ds['T2'].values)          # 2m 温度
print(ds.data_vars)
```

```python
# wrf-python 示例
from netCDF4 import Dataset
import wrf
nc = Dataset('wrfout_d01_2026-09-01_00:00:00')
slp = wrf.getvar(nc, 'slp')     # 海平面气压
wrf.cartopy_xlim(slp)
```

### 23.7 常用数据格式

| 格式 | 说明 | 查看工具 |
|---|---|---|
| NetCDF (.nc) | WRF 输入输出、大气科学标准格式 | ncdump、ncview、NCO、CDO |
| GRIB (.grb/.grb2) | 气象业务数据（如 GFS、ERA5） | wgrib2、grib_ls |
| HDF5 (.h5) | 科学数据通用格式 | h5ls、h5dump |
| 二进制 (.dat) | 无头信息，需说明文档 | od、xxd |

---

## 24. WRF 模型实战

### 24.1 WRF 简介

WRF（Weather Research and Forecasting）是下一代中尺度天气预报模式，广泛应用于科研与业务。编译运行依赖：
- **netCDF-C + netCDF-Fortran**：数据 I/O 库（WRF 的 Fortran 代码必须链接 Fortran 接口）
- **HDF5**：netCDF-4 底层存储库
- **zlib、libpng、Jasper**：GRIB2 压缩支持（WPS ungrib 处理 GRIB2 数据需要）
- **MPICH（或 OpenMPI）**：并行库
- **gcc、gfortran、make**：编译工具链

### 24.2 环境准备

```bash
# 系统工具
sudo apt update
sudo apt install -y build-essential gfortran cpp m4 csh tcsh \
    curl wget git unzip byacc flex bison libssl-dev libxml2-dev cmake

# 检查编译器
gcc --version
gfortran --version
make --version
```

### 24.3 目录规划与依赖库编译

```bash
export DIR=$HOME/Build_WRF
mkdir -p $DIR/src $DIR/LIBRARIES
cd $DIR/src
```

**1) 编译安装 netCDF（C 与 Fortran）**
```bash
cd $DIR/src
wget https://downloads.unidata.ucar.edu/netcdf-c/4.9.2/netcdf-c-4.9.2.tar.gz
wget https://downloads.unidata.ucar.edu/netcdf-fortran/4.6.1/netcdf-fortran-4.6.1.tar.gz
wget https://zlib.net/zlib-1.3.1.tar.gz
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.14/hdf5-1.14.3/src/hdf5-1.14.3.tar.gz
wget https://github.com/OSGeo/libpng/archive/refs/tags/v1.6.39.tar.gz
wget https://github.com/jasper-software/jasper/archive/refs/tags/version-2.0.33.tar.gz
wget https://www.mpich.org/static/downloads/4.2.3/mpich-4.2.3.tar.gz
```

按顺序编译：zlib → HDF5 → netCDF-C → netCDF-Fortran（netCDF-Fortran 依赖 C 库）。
```bash
# zlib
cd $DIR/src
tar -xzvf zlib-1.3.1.tar.gz && cd zlib-1.3.1
./configure --prefix=$DIR/grib2
make -j4 && make install

# HDF5
cd $DIR/src
tar -xzvf hdf5-1.14.3.tar.gz && cd hdf5-1.14.3
./configure --prefix=$DIR/grib2 --with-zlib=$DIR/grib2 --disable-shared
make -j4 && make install

# netCDF-C
cd $DIR/src
tar -xzvf netcdf-c-4.9.2.tar.gz && cd netcdf-c-4.9.2
CPPFLAGS=-I$DIR/grib2/include LDFLAGS=-L$DIR/grib2/lib \
    ./configure --prefix=$DIR/netcdf --disable-dap --disable-shared
make -j4 && make install

# netCDF-Fortran
cd $DIR/src
tar -xzvf netcdf-fortran-4.6.1.tar.gz && cd netcdf-fortran-4.6.1
CPPFLAGS=-I$DIR/netcdf/include LDFLAGS=-L$DIR/netcdf/lib \
    LIBS=-lnetcdf ./configure --prefix=$DIR/netcdf --disable-shared
make -j4 && make install
```

**2) 编译安装 MPICH**
```bash
cd $DIR/src
tar -xzvf mpich-4.2.3.tar.gz && cd mpich-4.2.3
./configure --prefix=$DIR/mpich
make -j4 && make install
```

**3) 配置环境变量（写入 ~/.bashrc 持久化）**
```bash
cat >> ~/.bashrc << 'EOF'
export DIR=$HOME/Build_WRF
export PATH=$DIR/netcdf/bin:$DIR/grib2/bin:$DIR/mpich/bin:$PATH
export NETCDF=$DIR/netcdf
export HDF5=$DIR/grib2
export JASPERLIB=$DIR/grib2/lib
export JASPERINC=$DIR/grib2/include
export LD_LIBRARY_PATH=$DIR/netcdf/lib:$DIR/grib2/lib:$LD_LIBRARY_PATH
EOF
source ~/.bashrc
```

> 版本号请以 WRF 官方在线教程（https://www2.mmm.ucar.edu/wrf/OnLineTutorial/）当前推荐版本为准。不同 WRF 版本对依赖库版本有兼容性要求，务必核对官方教程。

### 24.4 编译 WRF

```bash
cd $DIR
wget https://github.com/wrf-model/WRF/releases/download/v4.5.2/v4.5.2.tar.gz
tar -xzvf v4.5.2.tar.gz
cd WRF-4.5.2
./configure
```

`./configure` 会进入交互菜单，选择 **Fortran 编译器为 gcc (gfortran)、并行方式为 dmpar** 的选项。不同版本序号不同（WRF 4.x 中通常为 34 或 35 号附近），**务必以屏幕菜单实际显示的选项为准**，例如选 34 后提示 `Configuration successful`。

```bash
# 编译（em_real 是大气模式核心，含 real.exe 和 wrf.exe）
./compile em_real 2>&1 | tee compile.log

# 检查是否成功：main 目录下应存在 4 个可执行文件
ls -l main/*.exe
# wrf.exe  real.exe  ndown.exe  tc.exe
```

若缺文件，用 `grep -E "Error|错误" compile.log` 排查。

### 24.5 编译 WPS（前处理）

```bash
cd $DIR
wget https://github.com/wrf-model/WPS/releases/download/v4.5/v4.5.tar.gz
tar -xzvf v4.5.tar.gz
cd WPS-4.5
./configure
# 选择 gfortran + dmpar 对应选项（以菜单为准）
./compile 2>&1 | tee compile.log
ls geogrid.exe ungrib.exe metgrid.exe   # 三个都应存在
```

**下载静态地理数据**（geogrid 需要）：
```bash
cd $DIR
wget https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_complete.tar.gz
tar -xzvf geog_complete.tar.gz    # 解压出 WPS_GEOG 目录
```

### 24.6 WRF 标准运行流程

**第 1 步：geogrid（定义模拟区域，生成静态地形场）**
```bash
cd $DIR/WPS-4.5
vi namelist.wps     # 修改模拟区域（max_dom、e_we、e_sn、dx、dy、ref_lat、ref_lon 等）
./geogrid.exe       # 生成 geo_em.d01.nc（成功输出 Successful completion of geogrid）
```

**第 2 步：ungrib（解码 GRIB 气象数据）**
```bash
./link_grib.csh /path/to/your/gfs_files/*.grib2    # 链接 GRIB 数据
ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable    # 链接变量表（GFS 数据用 Vtable.GFS）
./ungrib.exe       # 生成 FILE:YYYY-MM-DD_HH 中间文件
```

**第 3 步：metgrid（水平插值到模式网格）**
```bash
vi namelist.wps    # 确认 fg_name = 'FILE'
./metgrid.exe      # 生成 met_em.d01.YYYY-MM-DD_HH.nc
```

**第 4 步：real（生成初始场与边界条件）**
```bash
cd $DIR/WRF-4.5.2/run
ln -sf /path/to/WPS/met_em.d01.* .
vi namelist.input  # 修改与 namelist.wps 一致的模拟区域、时间
./real.exe         # 生成 wrfinput_d01 和 wrfbdy_d01
```

**第 5 步：wrf（运行模式主程序）**
```bash
./wrf.exe
```

> dmpar 版本用 mpirun 并行运行：
> ```bash
> mpirun -np 8 ./real.exe
> mpirun -np 8 ./wrf.exe
> ```

### 24.7 运行结果检查

```bash
# 检查并行日志（dmpar 会生成 rsl.out.0000 等文件）
tail -20 rsl.out.0000
tail -20 rsl.error.0000

# 成功标志
grep "SUCCESS" rsl.out.0000
# real 成功: SUCCESS COMPLETE REAL_EM INIT
# wrf 成功:   SUCCESS COMPLETE WRF

# 检查输出文件
ls wrfout_d01_*    # 模式输出（每隔一定时间一个文件）
ncdump -h wrfout_d01_2026-09-01_00:00:00
```

### 24.8 常见错误与排查

| 现象 | 常见原因 | 排查方向 |
|---|---|---|
| `real.exe` 找不到文件 | met_em 未链接或 namelist 不一致 | 检查 run 目录下的 met_em 链接、时间设置 |
| CFL 错误 / 计算崩溃 | 时间步长太大 | 减小 `time_step`（建议 dx/（6×风速量级）） |
| 编译缺库 | 依赖库未安装或路径错 | 检查 NETCDF/HDF5/JASPERLIB 环境变量 |
| `configure` 找不到 Fortran | gfortran 未装 | `sudo apt install gfortran` |
| ungrib 报 GRIB2 错误 | Jasper/libpng 缺失 | 检查 JASPERLIB/JASPERINC 与 Vtable 链接 |
| 运行到一半 stopped | 磁盘满 / 内存不足 / 超过时限 | `df -h`、`free -h`、查看 rsl.error.0000 |

### 24.9 WRF 后处理

```bash
# 时间维度信息
ncdump -h wrfout_d01_* | head -50
# 变量裁剪与计算（NCO）
ncks -v T2,PSFC,RAINC wrfout_d01_* out.nc
# 可视化
ncview wrfout_d01_2026-09-01_00:00:00
# Python 后处理
conda activate wrf
python plot_wrf.py
```

**超算上提交 WRF 的 SLURM 脚本模板**：
```bash
#!/bin/bash
#SBATCH --job-name=wrf
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=48:00:00
#SBATCH --output=wrf_%j.out
#SBATCH --error=wrf_%j.err

cd $SLURM_SUBMIT_DIR
module load intel mpich netcdf   # 按平台环境修改
mpirun -np $SLURM_NTASKS ./wrf.exe
```

---

# 第五部分 求职与应试篇

## 25. 高频面试考点

### 25.1 场景题（必会）

**Q1：服务器 CPU/内存/磁盘满，如何排查？**
```bash
top          # CPU 占用，按 P 排序找占用最高进程
free -h      # 内存
df -h        # 磁盘空间
du -sh /*    # 定位大目录
ps aux --sort=-%mem | head   # 内存占用前几名
```

**Q2：某端口被占用，如何定位进程？**
```bash
ss -tulnp | grep 8080
lsof -i :8080
```

**Q3：如何查找某个文件？**
```bash
find / -name "wrfout*" 2>/dev/null
locate wrfout
```

**Q4：如何实时查看日志？**
```bash
tail -f /var/log/syslog
journalctl -f -u ssh
```

**Q5：如何找出并杀掉占用资源的进程？**
```bash
ps aux | grep python
kill -9 <PID>
```

### 25.2 概念题

**1. 软链接 vs 硬链接**
- 软链接：指向路径，可跨文件系统，可指目录，源删除则失效，有自己的 inode
- 硬链接：指向 inode，不可跨文件系统，不可指目录，源删除不影响

**2. 进程 vs 线程**
- 进程是资源分配的基本单位，有独立地址空间
- 线程是 CPU 调度的基本单位，共享进程地址空间

**3. 管道 vs 重定向**
- 管道 `|`：前命令输出作为后命令输入
- 重定向：改变输入/输出流向（文件等）

**4. 僵尸进程 vs 孤儿进程**
- 僵尸进程：子进程已退出但父进程未回收（wait），占用少量资源；用 `ps aux | grep Z` 查看
- 孤儿进程：父进程先退出，被 init（PID 1）收养

**5. inode 是什么**
- 存储文件元信息（权限、属主、大小、数据块指针）的数据结构，`ls -i` 查看 inode 号；`df -i` 查看 inode 使用

**6. 如何设置开机自启**
```bash
systemctl enable service
```

**7. 绝对路径与相对路径**
- 绝对路径从根 `/` 开始；相对路径相对当前目录

**8. `>` `>>` `2>&1` 区别**
- `>` 覆盖、`>>` 追加、`2>&1` 把标准错误并入标准输出

**9. 如何彻底删除用户**
```bash
sudo userdel -r username
```

**10. 查看系统版本**
```bash
cat /etc/os-release
uname -a
```

### 25.3 高频命令问答

| 问题 | 答案 |
|---|---|
| 查看端口监听 | `ss -tulnp` / `netstat -tulnp` |
| 查看进程 | `ps aux` / `top` |
| 查找文件 | `find` / `locate` |
| 查看文件内容 | `cat` / `less` / `tail` |
| 文本查找 | `grep` |
| 文本替换 | `sed 's/old/new/g'` |
| 按列处理 | `awk` |
| 压缩解压 | `tar -czvf` / `tar -xzvf` |
| 查看磁盘 | `df -h` |
| 查看目录大小 | `du -sh` |
| 远程拷贝 | `scp` / `rsync` |
| 查看内存 | `free -h` |
| 修改权限 | `chmod` |
| 定时任务 | `crontab -e` |
| 查看历史 | `history` |
| 查看系统负载 | `uptime` / `top` |

### 25.4 面试常问的 Linux 核心概念

- **发行版与内核**的区别
- **Shell 环境变量** PATH 的作用与修改
- **硬链接/软链接**区别（上文）
- **进程状态**（R/S/D/Z/T）
- **信号**（SIGTERM=15、SIGKILL=9）
- **文件系统挂载** mount/umount
- **swap 分区**的作用
- **静态库(.a) vs 动态库(.so)**：静态库链接进程序，动态库运行时加载（LD_LIBRARY_PATH）
- **DNS、DHCP 基本概念**
- **防火墙** ufw（Ubuntu）：`sudo ufw status`、`sudo ufw allow 22`

---

## 26. 常用命令速查表

### 26.1 文件与目录

| 命令 | 作用 |
|---|---|
| `ls` / `ls -la` | 列出 / 详细列出 |
| `cd` `pwd` | 切换 / 查看目录 |
| `mkdir -p` / `rmdir` | 创建 / 删除目录 |
| `cp -r` / `mv` / `rm -rf` | 复制 / 移动 / 删除 |
| `touch` | 创建空文件 |
| `ln -s` | 软链接 |
| `file` `stat` | 文件类型 / 元信息 |

### 26.2 文本查看与处理

| 命令 | 作用 |
|---|---|
| `cat` `less` `more` | 查看文件 |
| `head` `tail` | 首尾 N 行 |
| `tail -f` | 实时跟踪 |
| `wc -l` | 统计行数 |
| `sort` `uniq` | 排序 / 去重 |
| `cut` `paste` | 列操作 |
| `tr` | 字符转换 |
| `diff` | 文件比较 |

### 26.3 查找

| 命令 | 作用 |
|---|---|
| `find` | 按条件查找 |
| `grep` | 内容查找 |
| `which` `whereis` `locate` | 定位命令 / 文件 |

### 26.4 权限与用户

| 命令 | 作用 |
|---|---|
| `chmod` `chown` `chgrp` | 权限 / 属主 / 属组 |
| `useradd` `userdel` `usermod` | 用户管理 |
| `passwd` | 改密码 |
| `su` `sudo` | 切换 / 提权 |
| `id` `whoami` `who` | 身份查看 |

### 26.5 进程与系统

| 命令 | 作用 |
|---|---|
| `ps` `top` `htop` | 查看进程 |
| `kill` `pkill` `killall` | 终止进程 |
| `free` `df` `du` | 内存 / 磁盘 |
| `uptime` `uname` `lscpu` | 系统信息 |
| `nohup` `&` `jobs` `fg` `bg` | 后台任务 |

### 26.6 网络

| 命令 | 作用 |
|---|---|
| `ssh` | 远程登录 |
| `scp` `rsync` `sftp` | 文件传输 |
| `wget` `curl` | 下载 |
| `ping` `ip addr` `ss` | 网络诊断 |
| `hostname` | 主机名 |

### 26.7 软件与压缩

| 命令 | 作用 |
|---|---|
| `apt` `dpkg` | 软件管理 |
| `make` `make install` | 源码编译 |
| `conda` `pip` | Python 环境 |
| `tar` `gzip` `zip` | 压缩归档 |

### 26.8 服务与任务

| 命令 | 作用 |
|---|---|
| `systemctl` | 服务管理 |
| `journalctl` | 日志查看 |
| `crontab` | 定时任务 |
| `at` | 一次性任务 |

### 26.9 并行与科学计算

| 命令 | 作用 |
|---|---|
| `mpirun -np N` | MPI 并行运行 |
| `sbatch` `squeue` `sinfo` `scancel` `sacct` | SLURM 作业管理 |
| `module load` | 环境模块 |
| `ncdump` `ncview` `ncks` `cdo` | netCDF 数据处理 |
| `gfortran` `gcc` | 编译 |
| `nproc` `lscpu` | 查看核数 |

---

## 结语

这份指南覆盖了从基础命令到 WRF 实战的完整路径。建议学习路线：

1. **打基础**：掌握第一、二、三部分（命令、权限、系统管理、脚本）
2. **并行能力**：掌握第四部分 18-23 章（这是超算和科研求职的核心竞争力）
3. **结合科研**：按第 24 章完整走一遍 WRF 安装与运行流程
4. **应试准备**：用第 25-26 章做考前速查与自测

**学习建议**：任何命令都可以用 `man` 查询官方手册；多动手练习，多读日志，才是掌握 Linux 的最好方式。所有命令都建议先在本地 Ubuntu 虚拟机或实验机上验证后再用于生产环境。
