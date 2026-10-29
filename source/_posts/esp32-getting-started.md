---
title: 【ESP32 入门】开发环境搭建、烧录点灯与WIFI联网全流程
date: 2026-10-29 21:48:10
tags: [ESP32, 单片机, 物联网, C++]
categories:
    - 嵌入式
excerpt: 本文记录 ESP32 开发板基于 VS Code 与 PlatformIO 的环境搭建、工程创建、固件编译烧录、GPIO 点灯及 WiFi 联网的完整流程，并给出后续功能扩展方向。
---

# 一、概述

本文记录 ESP32 开发板的入门开发流程，内容包括开发环境搭建、工程创建、固件编译与烧录、
GPIO 输出测试、串口调试及 WiFi 连接。开发采用 **VS Code + PlatformIO IDE + Arduino 框架**的
组合：PlatformIO 集成了交叉编译工具链、烧录工具与依赖库管理，无需单独安装 Arduino IDE；
Arduino 框架 API 简洁，适合入门阶段使用。

# 二、硬件平台

## 2.1 开发板参数

所用开发板为通用 ESP32 DevKit，通过 USB-C 接口与计算机连接，板载 USB 转串口芯片为 CH340。
烧录时工具读取到的主控芯片为 `ESP32-D0WD-V3 rev 3.1`，硬件参数如下：

| 项目 | 参数 |
|---|---|
| 主控芯片 | ESP32-D0WD-V3 rev 3.1 |
| 内核 | 双核 Xtensa LX6，主频 240 MHz |
| Flash | 4 MB |
| 无线功能 | 2.4 GHz Wi-Fi、传统蓝牙（Bluetooth Classic）、BLE |
| USB 转串口 | CH340，设备管理器识别为 `USB-SERIAL CH340（COM7）` |
| 板载指示灯 | PWR 电源灯（红色）、D2 可编程指示灯（接 GPIO2） |
| 板载按键 | EN（复位）、BOOT（接 GPIO0） |

开发板实物如下图所示，模组丝印标注 `ESP-32`、`WiFi+BT SoC`，板上可识别 PWR、D2 两个指示灯
位、CH340 串口芯片、3.3V 稳压芯片以及 EN、BOOT 两个按键。

![ESP32 开发板实物](/img/esp32/board.jpg)

## 2.2 指示灯与按键说明

- **PWR 电源灯（红色）**：通电后常亮，仅作电源指示，不可由程序控制。
- **D2 可编程指示灯**：接 GPIO2，可由程序控制电平，用于 GPIO 输出测试及状态指示。
- **EN 按键**：复位键，按下后芯片复位并重新运行已烧录固件，不会清除固件。
- **BOOT 按键**：接 GPIO0。正常运行时可作为普通输入引脚；按住 BOOT 再短按 EN、随后松开 BOOT，
  可强制进入固件下载模式，用于处理烧录时无法自动进入下载状态的情况。

# 三、开发环境搭建

## 3.1 安装 PlatformIO 插件

在 VS Code 中按 `Ctrl+Shift+X` 打开扩展面板，搜索 `PlatformIO IDE` 并安装，安装完成后重启
VS Code。重启后通过 PlatformIO 图标进入 `PIO Home`，选择 `New Project` 创建工程。

## 3.2 创建工程

新建工程时的配置项如下：

- **Name**：工程名称。
- **Board**：选择实际开发板型号；通用 ESP32 DevKit 对应 `Espressif ESP32 Dev Module`（配置名
  `esp32dev`）。
- **Framework**：选择 `Arduino`。
- **Location**：工程路径，本文为 `C:\Code\EP32`。

首次创建工程时 PlatformIO 会自动下载工具链与 Arduino-ESP32 框架。实际安装的版本信息为：
PlatformIO Core 6.2.0、espressif32 平台 7.1.3、Arduino-ESP32 框架（PlatformIO 包版本
4.20017.260907，对应 arduino-esp32 核心 2.17.x）。

## 3.3 工程结构

工程目录结构如下：

```text
EP32/
├── .pio/            # 编译产物与构建缓存
├── src/
│   └── main.cpp     # 主程序文件
└── platformio.ini    # 工程配置文件
```

## 3.4 platformio.ini 配置

`platformio.ini` 用于指定平台、板型、框架及串口参数，本工程配置如下：

```ini
[env:esp32dev]
platform = espressif32        ; ESP32 平台
board = esp32dev              ; 板型：通用 ESP32 开发板
framework = arduino           ; Arduino 框架
upload_port = COM7            ; 烧录端口
monitor_port = COM7           ; 串口监视器端口
monitor_speed = 115200        ; 串口波特率
```

PlatformIO 通常可自动识别串口，识别失败时再通过 `upload_port`、`monitor_port` 手动指定。
若创建工程时选择的是其他板型，应保留其自动生成的 `board` 配置，ESP32、ESP32-C3、ESP32-S3
的板型配置不可混用。

# 四、GPIO 输出测试：LED 闪烁

## 4.1 测试程序

第一项测试为控制 GPIO2 上的 D2 指示灯周期性翻转，同时通过串口输出芯片信息与引脚状态。
将 `src/main.cpp` 编写为：

```cpp
#include <Arduino.h>

constexpr uint8_t LED_PIN = 2;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  delay(1000);
  Serial.println("\nESP32 test started");
  Serial.printf("Chip model: %s\n", ESP.getChipModel());
  Serial.printf("CPU frequency: %u MHz\n", ESP.getCpuFreqMHz());
  Serial.printf("Flash size: %u MB\n", ESP.getFlashChipSize() / 1024 / 1024);
}

void loop() {
  static bool ledOn = false;
  ledOn = !ledOn;
  digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
  Serial.printf("GPIO2 LED: %s | uptime: %lu ms\n", ledOn ? "ON" : "OFF", millis());
  delay(500);
}
```

Arduino 程序由两个核心函数构成：`setup()` 在上电或复位后执行一次，用于初始化；`loop()` 在
`setup()` 执行完成后循环运行，用于承载主逻辑。程序中通过 `pinMode()` 将 GPIO2 配置为输出模式，
通过 `digitalWrite()` 改变引脚电平，实现 LED 的点亮与熄灭。

## 4.2 编译与烧录

VS Code 底部状态栏提供 Build、Upload、Serial Monitor 三个操作入口，对应开发流程为：

```text
编写代码 → 编译 Build → 上传 Upload → 芯片复位运行 → 串口监视器查看输出
```

操作步骤：点击 Build，输出 `SUCCESS` 表示编译通过；点击 Upload，固件经 COM7 烧录并自动校验、
复位；打开 Serial Monitor 查看串口输出。烧录完成后生成的 `firmware.bin` 约 716 KB。

## 4.3 测试结果

烧录后 D2 指示灯以 500 ms 为间隔交替点亮、熄灭，串口同步输出引脚状态与运行时间，表明
“编译 → 烧录 → 芯片运行 → GPIO 输出”链路工作正常。实测效果如下（视频前 1.5 s 截取）：

![D2 指示灯闪烁实测](/img/esp32/led-blink.gif)

# 五、WiFi 连接

## 5.1 连接前提

经典 ESP32 仅支持 **2.4 GHz Wi-Fi**，无法连接仅开启 5 GHz 的网络，连接前需确认路由器或热点
已启用 2.4 GHz 频段。Arduino 框架已内置 WiFi 库，无需额外安装依赖。

## 5.2 连接程序

以 STA（Station，站点）模式连接路由器，将 `src/main.cpp` 替换为：

```cpp
#include <Arduino.h>
#include <WiFi.h>

constexpr uint8_t LED_PIN = 2;

// 仅在本地填写，禁止将含密码的代码提交至公开仓库。
const char* WIFI_SSID = "2.4GHz WiFi 名称";
const char* WIFI_PASSWORD = "WiFi 密码";

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  WiFi.mode(WIFI_STA);
  WiFi.setHostname("esp32-board");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.printf("\nConnecting to %s", WIFI_SSID);

  // 最多等待 20 秒，等待期间 D2 快速闪烁。
  for (int i = 0; i < 80 && WiFi.status() != WL_CONNECTED; ++i) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(250);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    digitalWrite(LED_PIN, LOW);
    Serial.println("\nConnection failed; check SSID, password and 2.4GHz.");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // 连接正常时 D2 每秒翻转一次。
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));

    Serial.printf(
        "WiFi OK | IP: %s | RSSI: %d dBm\n",
        WiFi.localIP().toString().c_str(),
        WiFi.RSSI());

    delay(1000);
  } else {
    digitalWrite(LED_PIN, LOW);
    Serial.println("WiFi disconnected; reconnecting...");
    WiFi.reconnect();
    delay(5000);
  }
}
```

`setup()` 中通过 `WiFi.begin()` 发起连接，并以最多 20 s 的循环等待连接结果；`loop()` 中通过
`WiFi.status()` 判断连接状态，在线时周期性输出 IP 与信号强度，掉线时调用 `WiFi.reconnect()`
重连。

## 5.3 测试结果

烧录后开发板成功连接 2.4 GHz 热点，串口输出获取到的局域网 IP 与信号强度，连接正常时 D2
每秒翻转一次，表明 WiFi 联网功能工作正常。串口输出示例：

```text
WiFi connected
IP address: 192.168.x.x
WiFi OK | IP: 192.168.x.x | RSSI: -45 dBm
```

`WiFi.localIP()` 返回路由器分配的局域网 IP 地址，`WiFi.RSSI()` 返回信号强度（单位 dBm，数值越
接近 0 信号越强）。WiFi 密码仅在本地代码中填写，不应在公开仓库中泄露。

# 六、后续开发方向

在 GPIO 点灯验证通过的基础上，后续可沿无线通信与外设扩展两个方向继续开发。无线通信方面，
可利用芯片内置的 2.4 GHz Wi-Fi 实现 STA 联网、网页控制与数据上传，或利用蓝牙/BLE 与手机
通信；外设方面，可接入 I²C OLED 显示屏（如 SSD1306）独立显示状态信息，接入 I²S 麦克风
（如 INMP441）与功放扬声器（如 MAX98357A）实现音频采集与播放，也可进一步接入温湿度等
传感器，组合构成环境监测、网页点灯、网络状态监测等简易工具。

待 Arduino 框架下的基础功能开发熟练后，可进一步学习官方 ESP-IDF 框架，以使用 FreeRTOS、
低功耗管理及更完整的底层能力。文中引脚定义与版本号均来自实际环境，不同开发板可能存在差异，
实际接线前应对照原理图确认。
