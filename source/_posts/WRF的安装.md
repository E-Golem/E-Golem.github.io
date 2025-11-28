---
title: WRF在Linux系统下的安装教程（手动编译）
tags: [WRF,Linux]
date: 2025-11-10
excerpt: WPS的运行
banner_img: /img/wrf.png
categories: 
    - WRF
---

### I、首先是获取安装WRF需要的相关的软件包

批量解压压缩包到特定文件夹中

```bash
cd ./zhang/Lib
#进入存放压缩包的目录
for gz_file in *.gz; do
    # 获取不带扩展名的文件名
    dir_name="${gz_file%.gz}"
    
    # 创建文件夹
    mkdir -p "$dir_name"
    
    # 解压到对应文件夹
    tar -xzvf $gz_file -C ~/zhang/Lib/$dir_name
    echo "已解压 $gz_file 到文件夹 $dir_name/"
done
```

### II、首先安装编译器（intel系列或者gcc系列）

这里选择安装gcc编译器，注意一定要使用合适版本的编译器（WRF4.0对应大概是gcc-7.3.0），可以避免很多错误
首先需要安装依赖，运行

```bash
./contrib/download_prerequisites
```

创建build文件夹并进入
前面的操作还是老一套configure ，make ，make install三步走

```bash
../configure \
    --prefix=/home/zhangpengwen/palwe/app/gcc-7.3.0 \
    --enable-checking=release \
    --enable-languages=c,c++,fortran \
    --disable-multilib
```

安装成功后添加环境变量到bashrc

```bash
export GCCROOT=/app/gcc-7.3.0
```

之后可以使用gcc -v来确定是否安装成功以及是否是你刚刚安装的路径

出现问题
1、由于在运行configure时出现问题，发现问题的根源来自之前设置的环境变量LIBS，以下是AI的解释：
  
LIBS 环境变量是什么？
LIBS 是一个专门用于编译和链接程序的便利贴（环境变量）。

它的名字 LIBS 是 "Libraries"（库）的缩写。

当这个变量被设置时，它会告诉 configure 脚本、make 工具链或编译器（如 gcc）：“嘿，当你要把程序链接（Link）成一个可执行文件时，除了你正常需要链接的库之外，务必也要把我便利贴上写的这些库（比如 -lgeotiff, -ltiff）一起链接进去。”

可使用 ```unset LIBS\LDFLAGS\CFLAGS```指令先把环境变量去除

2、其次，conda环境下也会导致编译出现问题（需要c语言环境），因此需要退出conda环境，使用```conda deactivate```退出conda，首次退出当前环境会退回到base环境，需要再退出一次

### III、按顺序安装其他软件

这里可以专门创建一个目录用来存放所有软件的bin，lib，include，方便后续指定路径，比如在根目录下创建目录app，后续安装路径全都指定到这个目录下

#### 1、安装zlib

#### 2、安装szip软件，配置时加上 --enable-shared

#### 3、hdf5的安装需要上面个两个作为依赖

```bash
./configure --enable-shared --enable-fortran --with-zlib=/home/zhangpengwen/palwe/app/ --with-szip=/home/zhangpengwen/palwe/app/ --prefix=/home/zhangpengwen/palwe/app/
```

时间会比较久

#### 4、安装udunits2

如果有管理员权限，可以直接使用apt(unbuntu)命令下载 expat* 所有相关库
如果没有管理员权限，可以使用conda安装，执行

```bash
conda install -c conda-forge expat
```

安装完成后，配置环境变量：

```bash
export CPPFLAGS="-I$CONDA_PREFIX/include $CPPFLAGS"
export LDFLAGS="-L$CONDA_PREFIX/lib $LDFLAGS"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
```

注意这一步要在conda环境下进行，否则无法找到conda路径

之后老套路安装，不过依然要加上动态库

#### 5、安装netcdf-c

```bash
./configure --enable-shared --enable-netcdf4 CPPFLAGS=-I/home/zhangpengwen/palwe/app/include --prefix=/home/zhangpengwen/palwe/app/ LDFLAGS=-L/home/zhangpengwen/palwe/app/lib
```

**tips: 运行configure时，--是程序自己的选项，其他的类似CPPFLAGS是给变量赋值，因此不用加--**

又报错了，这次是说缺少m4这个工具，依旧用conda安装

```bash
conda install -c conda-forge m4
```

成功安装后即可顺利安装netcdf-c

#### 6、安装netcdf-fortran

```bash
export LD_LIBRARY_PATH=/home/zhangpengwen/palwe/app/lib/:${LD_LIBARY_PATH}
```

首先设置环境变量，告诉系统找依赖的libary都去这个路径下去找
后续步骤同上，不过 --enable-netcdf4 要删除

#### 7、安装netcdf-cxx

安装步骤同上，不再赘述

#### 8、安装libpng

基本操作，连接上动态库即可

#### 9、安装jasper

同上

#### 10、安装mpich

装到最后才发现少装了一个，本来是写在后面的，怕影响后续的安装，放到前面来了
加入了环境变量

```bash
export CC=/home/zhangpengwen/palwe/app/gcc-13.3.0/bin/gcc
export CXX=/home/zhangpengwen/palwe/app/gcc-13.3.0/bin/g++
export FC=/home/zhangpengwen/palwe/app/gcc-13.3.0/bin/gfortran
export F77=$FC
export FFLAGS="-w -fallow-argument-mismatch -O2"
export FCFLAGS="-w -fallow-argument-mismatch -O2"
```

虽然笔者是按这段命令安装的，但是这是由于笔者的gcc版本太高造成的版本冲突，CFLAGS="-fcommon" CXXFLAGS="-fcommon" 这一行版本合适的话大概率不需要，因此仅供参考。

```bash
CFLAGS="-fcommon" CXXFLAGS="-fcommon" \
    ./configure --prefix=/app/ --enable-shared
make -j 8
make install
```

#### 11、后处理软件的安装，不影响WRF的安装，可以先跳过（cdo.ncview,nco）

本来笔者也想是下载源码包编译安装这些后处理软件，但是由于配置各种依赖，还要解决版本冲突的问题，这里不如直接使用conda安装这些软件，并不影响软件的使用。
不过这里尽量建立独立的虚拟环境安装这些软件，不要一股脑全部安装到base环境中，建立独立conda环境的操作这里不再赘述。

进入你的conda环境，运行

```bash
conda install -c conda-forge ncl cdo ncview
```

conda会自动下载所有相关的依赖

#### 12、安装WRF

安装需要在conda环境下
在.bashrc中加入环境变量

```bash
export PATH=/home/zhangpengwen/palwe/app/bin:${PATH}
export LD_LIBRARY_PATH=/home/zhangpengwen/palwe/app/lib/:${LD_LIBARY_PATH}
export NETCDF=/home/zhangpengwen/palwe/app/
export JASPERLIB=/home/zhangpengwen/palwe/app/lib
export JASPERINC=/home/zhangpengwen/palwe/app/include
```

之后执行 source ./.bashrc 使得环境变量生效
为WRF的安装指定依赖路径

然后开始安装WRF
直接执行 ./configure
会弹出很多选项：
![选项](img/wrf/wrf/install.png)

不同列代表不同的并行模式，一般使用第三列（dmpar）
不同行代表不同编译器，在这里我们使用的时GUN，因此选择34
之后会出现

```bash
Compile for nesting? (1=basic, 2=preset moves, 3=vortex following) [default 1]: 
```

直接回车，这里会测试编译器和netcdf是否兼容

之后执行

```bash
./compile em_real >& compile.log
```

这里由于执行了 >& compile.log 因此输出和报错不会出现在屏幕上，而是被保存成日志文件，这是由于在编译大型文件时由于信息太快不易发现错误，因此保存日志方便查找error出现的位置

-------------以下是修正部分，仅供参考,不需要照做---------------------------------------------------------------------------------------------
发现编译错误了，查找原因发现（grep -i "Fatal" compile.log）是找不到 mpif.h 文件，最后发现还是环境变量的问题,configure找到的是conda里的mpif90，然而conda没有安装编译器

安装mpich时 configure出现错误，原因是gcc编译器版本太高，导致把一些旧写法识别为了错误导致configure报错
解决办法：1）安装更新的mpich版本（可能会存在其他的依赖问题）2）告诉编译器忽略这个错误
这里采用第二种办法

```bash
export CC=/home/zhangpengwen/palwe/app/gcc-13.3.0/bin/gcc
export CXX=/home/zhangpengwen/palwe/app/gcc-13.3.0/bin/g++
export FC=/home/zhangpengwen/palwe/app/gcc-13.3.0/bin/gfortran
export F77=$FC
export FFLAGS="-w -fallow-argument-mismatch -O2"
export FCFLAGS="-w -fallow-argument-mismatch -O2"
```

make编译时又出错了，这里是由于高版本的gcc修改了默认选项从 -fcommon 变成了 -fno-common,使用下面指令修改

```bash
CFLAGS="-fcommon" CXXFLAGS="-fcommon" \
    ./configure --prefix=/app/ --enable-shared
make -j 8
make install
```

成功安装，可以使用which指令看一下是否能在安装目录下找到mpif90

export PATH=/home/zhangpengwen/palwe/app/bin:$PATH

ln -s /home/zhangpengwen/palwe/app/include/mpif.h mpif.h

然而最终没有解决

------------------修正结束，一次失败的修正--------------------------------------------------------------------------------------------------

最终解决方案：
1、退出conda环境，configure时会出现报错说找不到m4，这里是因为当初是把m4安装到了conda下，所以说在安装依赖时一定不要在多个环境下安装，而且不建议全部都在conda中安装
使用wget下载m4源码包即可下载
wget http://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.gz
之后还按之前的步骤安装

2、修改configure.wrf以下几行

```bash
FC              =       $(DM_FC)
LIB_EXTERNAL    = \
                      -L$(WRF_SRC_ROOT_DIR)/external/io_netcdf -lwrfio_nf -L/home/zhangpengwen/palwe/app/lib -lnetcdff -lnetcdf -lhdf5_hl -lhdf5 -lz
FCBASEOPTS_NO_G = -w $(FORMAT_FREE) $(BYTESWAPIO) -fallow-argument-mismatch -fallow-invalid-boz
```

**注意，这里只代表我这里出现的问题可以这样解决，并且中间有部分其他修改步骤未作记录，因此只供参考，具体问题再去自行查找(另外进一步证明了gemini比gpt好用)**

最后出现
Executables successfully built
即说明安装成功

可以尝试运行生成的可执行程序来测试是否安装成功：

```bash
cd run
./wrf.exe
```

当然运行是不可能成功的，但是证明成功安装了

#### 13、WPS的安装

注意，虽然作为WRF的前处理系统，但是WPS是要放在WRF之后安装的，因为WPS安装时需要找到WRF的位置

首先依旧是运行

```bash
./configure
./compile &> log.compile
```

依旧会有选项，跟WRF一样，按实际情况选择，这里选择3
![选项](img/wrf/wps/install.png)

这里果不其然出现了报错，查了一圈发现还是gcc版本太高了，所以建议一开始一定要用合适版本的编译器
当然还有一个错误就是找不到WRF，这个比较好改，改一下configure.wps里WRF的路径就行，或者直接按configure里WRF的路径修改自己WRF的路径（一般是跟WPS在同目录下，命名为WRF/WRFV3）

之后继续修改configure.wps文件,让gcc忽略版本差异造成的错误
修改下面两行成：

```bash
FFLAGS              = -ffree-form -O -fconvert=big-endian -frecord-marker=4 -fallow-argument-mismatch -fallow-invalid-boz -std=legacy
F77FLAGS            = -ffixed-form -O -fconvert=big-endian -frecord-marker=4 -fallow-argument-mismatch -fallow-invalid-boz -std=legacy
```

当然还没有结束，因为又报错了，这次是ungrib无法正常编译，其他两个exe都编译出来了。错误是版本过高导致有些错误无法忽略，因此要修改源码，不过不复杂。

打开 ungrib/src/ngl/g2/intmath.f

```bash
vi ungrib/src/ngl/g2/intmath.f
```

找到172行和207左右的

```bash
if(iand(i,i-1)/=0) then
```

修改为

```bash
if(iand(i, int(i-1, kind(i))) /= 0) then
```

保存之后清理编译缓存:

```bash
cd ungrib/src/ngl/g2
make clean
rm -f *.o *.mod
cd ../../../..
# 现在你应该回到了 WPS-4.0 根目录
```

之后重新编译即可，笔者这里是直接成功了，还是一样，可以看到WPS根目录下生成了三个exe程序就说明编译成功了，也可以尝试运行测试一下

OK，到这里就完成了WRF的安装全流程，接下来就可以直接跑了。
