---
title: 深度学习学习记录
tags: [python,Deep Learning]
date: 2025-9-16
excerpt: 深度学习学习记录1
banner_img: /img/dpln/dl.jpg
categories: 
    - Deep Learning
    - pytorch入门
---
深度学习学习记录 [RethinkFun深度学习教程](https://www.rethink.fun/)

*****

## Tensor张量

是一种多为数组 可用torch或者numpy创建，Tensor属性类似numpy数组
Tensor数据类型：整形，浮点型，布尔型
```python
torch.tensor(data)
np.ndarray(data)
```


Tensor的统计操作和切片索引：

```python
torch.tensor([[1, 2, 3],[1, 2, 3]],dtype=torch.float32)
print(t1.mean(dim=0))#选择维度 0为行
print(t1[1,0])
```

Tensor利用GPU加速计算

```python
t1 = torch.randn((3,4),device="cuda")#创建到GPU
t1 = t1.to("cpu")#转移到GPU
```

## pytorch梯度计算与线性回归

- 梯度计算
  
```python
import torch

x = torch.tensor(1.0, requires_grad=True) #指定需要计算梯度
y = torch.tensor(1.0, requires_grad=True) #指定需要计算梯度
v = 3*x+4*y
u = torch.square(v)
z = torch.log(u)

z.backward() #反向传播求梯度

print("x grad:", x.grad)
print("y grad:", y.grad)
```

输出结果为
x grad: tensor(0.8571)
y grad: tensor(1.1429)

- 线性回归：

```python
import torch

# 确保CUDA可用
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 生成数据
inputs = torch.rand(100, 3) # 生成shape为(100,3)的tensor，里边每个元素的值都是0-1之间
weights = torch.tensor([[1.1], [2.2], [3.3]])
bias = torch.tensor(4.4)
targets = inputs @ weights + bias + 0.1*torch.randn(100, 1) #增加一些随机，模拟真实情况


# 初始化参数时直接放在CUDA上，并启用梯度追踪
w = torch.rand((3, 1), requires_grad=True, device=device)
b = torch.rand((1,), requires_grad=True, device=device)

# 将数据移至相同设备
inputs = inputs.to(device)
targets = targets.to(device)

epoch = 10000
lr = 0.003

for i in range(epoch):
    outputs = inputs @ w + b
    loss = torch.mean(torch.square(outputs - targets))
    print("loss:", loss.item())

    loss.backward()

    with torch.no_grad(): #下边的计算不需要跟踪梯度
        w -= lr * w.grad
        b -= lr * b.grad

    # 清零梯度，否则梯度会累加
    w.grad.zero_()
    b.grad.zero_()

print("训练后的权重 w:", w)
print("训练后的偏置 b:", b)
```

输出结果：
训练后的权重 w: tensor([[1.1682],
        [2.2172],
        [3.3188]], device='cuda:0', requires_grad=True)
训练后的偏置 b: tensor([4.3380], device='cuda:0', requires_grad=True)

## tensorboard绘制loss曲线

首先安装tensorboard库
运行[代码](https://github.com/E-Golem/DeepLearning/blob/master/chapter6/LossChart.py)
命令行输入: tensorboard --logdir=保存的地址,之后打开localhost即可查看loss曲线

## 归一化

不同特征的取值范围不同，对loss函数的影响不同（梯度的影响不同），在共用学习率lr的情况下，会使得loss函数无法接近理想值。
归一化常用特征值/特征最大值，这样所有值都分布在[0,1]之间了（同样的也可标准化处理，即特征值-平均值/标准差，使数据分布在[-1,1]之间）

```python
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
inputs = torch.tensor([[2, 1000], [3, 2000], [2, 500], [1, 800], [4, 3000]], dtype=torch.float, device=device)
labels = torch.tensor([[19], [31], [14], [15], [43]], dtype=torch.float, device=device)

#进行归一化
inputs = inputs / torch.tensor([4, 3000], device=device)


w = torch.ones(2, 1, requires_grad=True, device=device)
b = torch.ones(1, requires_grad=True, device=device)

epoch = 1000
lr = 0.5

for i in range(epoch):
    outputs = inputs @ w + b
    loss = torch.mean(torch.square(outputs - labels))
    print("loss", loss.item())
    loss.backward()
    print("w.grad", w.grad.tolist())
    with torch.no_grad():
        w -= w.grad * lr
        b -= b.grad * lr

    w.grad.zero_()
    b.grad.zero_()
```

输出结果可以发现loss函数很接近0，符合预设的函数特性