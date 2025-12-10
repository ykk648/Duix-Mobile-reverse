# Duix-Android NCNN 模型推理分析

## 📋 目录

1. [项目结构](#项目结构)
2. [核心代码文件](#核心代码文件)
3. [模型加载流程](#模型加载流程)
4. [数据预处理](#数据预处理)
5. [模型推理](#模型推理)
6. [完整调用流程](#完整调用流程)
7. [关键技术点](#关键技术点)

---

## 项目结构

```
duix-android/dh_aigc_android/duix-sdk/src/main/
├── java/ai/guiji/duix/
│   └── DuixNcnn.java                    # Java 层 JNI 接口
├── cpp/
│   ├── android/
│   │   └── DuixJni.cpp                  # JNI 实现层
│   ├── duix/
│   │   ├── gjduix.cpp                   # 音频处理模块
│   │   └── gjsimp.cpp                   # 主要推理封装
│   ├── dhunet/
│   │   ├── munet.h                      # NCNN 模型类头文件
│   │   ├── munet.cpp                    # NCNN 模型推理实现
│   │   ├── blendgram.cpp/h              # Alpha 混合算法
│   │   ├── malpha.cpp/h                 # Alpha 通道处理
│   │   ├── jmat.cpp/h                   # 矩阵封装类
│   │   └── face_utils.cpp/h             # 人脸工具函数
│   ├── dhmfcc/
│   │   ├── dhpcm.cpp/h                  # PCM 音频处理
│   │   ├── dhwenet.cpp/h                # WeNet 音频特征提取
│   │   └── wenetai.cpp/h                # WeNet AI 推理
│   ├── include/
│   │   ├── gjduix.h                     # 对外接口定义
│   │   └── gjsimp.h                     # 简化接口定义
│   └── third/
│       └── ncnn-20231027-android-shared/ # NCNN 库
```

---

## 核心代码文件

### 1. Java 层接口 - `DuixNcnn.java`

```java
package ai.guiji.duix;

public class DuixNcnn {
    // 初始化和资源管理
    public native int alloc(int taskid, int mincalc, int width, int height);
    public native int free(int taskid);
    
    // 模型初始化
    public native int initPcmex(int maxsize, int minoff, int minblock, int maxblock, int rgb);
    public native int initWenet(String fnwenet);
    public native int initMunet(String fnparam, String fnbin, String fnmask);
    public native int initMunetex(String fnparam, String fnbin, String fnmask, int kind);
    
    // 会话管理
    public native long newsession();
    public native int finsession(long sessid);
    public native int consession(long sessid);
    
    // 数据处理
    public native int allcnt(long sessid);
    public native int readycnt(long sessid);
    public native int pushpcm(long sessid, byte[] arrbuf, int size, int kind);
    
    // 推理接口
    public native int filerst(long sessid, String picfn, String mskfn,
        int[] arrbox, String fgpic, int index, byte[] arrimg, byte[] arrmsk, int imgsize);
    public native int bufrst(long sessid, int[] arrbox, int index, byte[] arrimg, int imgsize);
    
    // 文件加载
    public native int fileload(String picfn, String mskfn, int width, int height,
         byte[] arrpic, byte[] arrmsk, int imgsize);
    
    static {
        System.loadLibrary("gjduix");
    }
}
```

### 2. NCNN 模型类 - `munet.h`

```cpp
#pragma once
#include "jmat.h"
#include "net.h"
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

class Mobunet {
private:
    int m_wenetstep = 20;
    int m_rgb = 0;
    ncnn::Net unet;                              // NCNN 网络对象
    float mean_vals[3] = {127.5f, 127.5f, 127.5f};
    float norm_vals[3] = {1/127.5f, 1/127.5f, 1/127.5f};
    JMat* mat_weights = nullptr;                 // 160x160 权重矩阵
    JMat* mat_weightmin = nullptr;               // 128x128 权重矩阵
    int initModel(const char* binfn, const char* paramfn, const char* mskfn);

public:
    int domodel(JMat* pic, JMat* msk, JMat* feat, int rect = 160);
    int preprocess(JMat* pic, JMat* feat);
    int process(JMat* pic, const int* boxs, JMat* feat);
    int fgprocess(JMat* pic, const int* boxs, JMat* feat, JMat* fg);
    Mobunet(const char* fnbin, const char* fnparam, const char* fnmsk, 
            int wenetstep = 20, int rgb = 0);
    ~Mobunet();
};
```

---

## 模型加载流程

### 初始化代码 - `munet.cpp`

```cpp
int Mobunet::initModel(const char* binfn, const char* paramfn, const char* mskfn) {
    unet.clear();
    
    // 配置 NCNN 选项
    unet.opt.use_vulkan_compute = false;           // 不使用 Vulkan
    unet.opt.num_threads = ncnn::get_big_cpu_count(); // 使用大核数量
    
    // 加载模型文件
    unet.load_param(paramfn);  // 加载 .param 文件（文本格式的网络结构）
    unet.load_model(binfn);    // 加载 .bin 文件（二进制格式的权重数据）
    
    // 注：如果使用二进制格式的 param，则调用：
    // unet.load_param_bin(paramfn);  // 加载 .param.bin 文件
    
    // 加载 mask 权重文件
    char* wbuf = NULL;
    dumpfile((char*)mskfn, &wbuf);
    printf("===mskfn %s\n", mskfn);
    
    // 创建 160x160 权重矩阵
    mat_weights = new JMat(160, 160, (uint8_t*)wbuf, 1);
    mat_weights->forceref(0);
    
    // 创建 128x128 权重矩阵（缩放版本）
    mat_weightmin = new JMat(128, 128, 1);
    cv::Mat ma = mat_weights->cvmat();
    cv::Mat mb;
    cv::resize(ma, mb, cv::Size(128, 128));
    cv::Mat mc = mat_weightmin->cvmat();
    mb.copyTo(mc);
    
    return 0;
}
```

### 构造函数

```cpp
Mobunet::Mobunet(const char* fnbin, const char* fnparam, const char* fnmsk, 
                 int wenetstep, int rgb) {
    m_rgb = rgb;
    m_wenetstep = wenetstep;
    initModel(fnbin, fnparam, fnmsk);
}
```

---

## 数据预处理

### 预处理流程 - `munet.cpp::domodel()`

```cpp
int Mobunet::domodel(JMat* pic, JMat* msk, JMat* feat, int rect) {
    int width = pic->width();
    int height = pic->height();
    
    // 1️⃣ 加载并预处理 mask 图像
    ncnn::Mat inmask = ncnn::Mat::from_pixels(
        msk->udata(), 
        m_rgb ? ncnn::Mat::PIXEL_RGB : ncnn::Mat::PIXEL_BGR2RGB, 
        rect, rect
    );
    inmask.substract_mean_normalize(mean_vals, norm_vals);
    
    // 2️⃣ 加载并预处理真实图像
    ncnn::Mat inreal = ncnn::Mat::from_pixels(
        pic->udata(), 
        m_rgb ? ncnn::Mat::PIXEL_RGB : ncnn::Mat::PIXEL_BGR2RGB, 
        rect, rect
    );
    inreal.substract_mean_normalize(mean_vals, norm_vals);
    
    // 3️⃣ 合并为 6 通道输入（3通道真实图 + 3通道mask）
    ncnn::Mat inpic(width, height, 6);
    float* buf = (float*)inpic.data;
    float* pr = (float*)inreal.data;
    memcpy(buf, pr, inreal.cstep * sizeof(float) * inreal.c);
    buf += inpic.cstep * inreal.c;
    float* pm = (float*)inmask.data;
    memcpy(buf, pm, inmask.cstep * sizeof(float) * inmask.c);
    
    // 4️⃣ 准备音频特征（WeNet 特征）
    float* pf = (float*)feat->data();
    if (m_wenetstep == 10) {
        pf += 256 * 5;  // 偏移到特定位置
    }
    ncnn::Mat inwenet(256, m_wenetstep, 1, pf);
    
    // ... 后续推理流程
}
```

### 归一化参数说明

```cpp
// 均值和标准差
float mean_vals[3] = {127.5f, 127.5f, 127.5f};
float norm_vals[3] = {1/127.5f, 1/127.5f, 1/127.5f};

// 归一化公式：output = (input - mean) * norm
// 即：output = (input - 127.5) * (1/127.5)
// 将 [0, 255] 映射到 [-1, 1]
```

---

## 模型推理

### 推理执行代码

```cpp
int Mobunet::domodel(JMat* pic, JMat* msk, JMat* feat, int rect) {
    // ... 前面的预处理代码 ...
    
    // 5️⃣ 创建推理提取器
    ncnn::Extractor ex = unet.create_extractor();
    
    // 6️⃣ 设置输入张量
    ex.input("face", inpic);      // 输入1: 6通道图像
    ex.input("audio", inwenet);   // 输入2: 音频特征
    
    // 7️⃣ 执行推理
    ncnn::Mat outpic;
    ex.extract("output", outpic);
    
    // 8️⃣ 后处理：反归一化
    float outmean_vals[3] = {-1.0f, -1.0f, -1.0f};
    float outnorm_vals[3] = {127.5f, 127.5f, 127.5f};
    outpic.substract_mean_normalize(outmean_vals, outnorm_vals);
    
    // 9️⃣ 转换回 OpenCV 格式
    cv::Mat cvout(width, height, CV_8UC3);
    outpic.to_pixels(
        cvout.data, 
        m_rgb ? ncnn::Mat::PIXEL_RGB : ncnn::Mat::PIXEL_RGB2BGR
    );
    
    // 🔟 Alpha 混合：将推理结果与原图融合
    if (rect == 160) {
        BlendGramAlpha(
            (uchar*)cvout.data,
            (uchar*)mat_weights->data(),
            (uchar*)pic->data(),
            width, height
        );
    } else {
        BlendGramAlpha(
            (uchar*)cvout.data,
            (uchar*)mat_weightmin->data(),
            (uchar*)pic->data(),
            width, height
        );
    }
    
    return 0;
}
```

### 推理性能监控 - `gjsimp.cpp`

```cpp
int dhduix_simprst(dhduix_t* dg, uint64_t sessid, uint8_t* bpic, 
                   int width, int height, int* box, 
                   uint8_t* bmsk, uint8_t* bfg, 
                   uint8_t* bnfbuf, int bnflen) {
    // ... 准备工作 ...
    
    // 推理计时
    uint64_t ticka = jtimer_msstamp();
    rst = dg->munet->domodel(mpic, mmsk, feat, dg->rect);
    uint64_t tickb = jtimer_msstamp();
    uint64_t dist = tickb - ticka;
    
    // 性能日志
    if (dist > 40) {  // 超过 40ms 记录日志
        printf("===domodel %d dist %ld\n", rst, dist);
    }
    
    // ... 后处理 ...
}
```

---

## 完整调用流程

### 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      1. 初始化阶段                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: scrfdncnn.alloc(0, 20, width, height)
                              │
                              ▼
    JNI: Java_ai_guiji_duix_DuixNcnn_alloc()
                              │
                              ▼
    C++: dhduix_alloc(&g_digit, mincalc, width, height)
                              │
                              ▼
    创建 dhduix_t 结构体，分配内存

┌─────────────────────────────────────────────────────────────┐
│                    2. 模型加载阶段                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: scrfdncnn.initMunet(param, bin, mask)
                              │
                              ▼
    JNI: Java_ai_guiji_duix_DuixNcnn_initMunet()
                              │
                              ▼
    C++: dhduix_initMunet()
                              │
                              ▼
    创建 Mobunet 对象
                              │
                              ▼
    Mobunet::initModel()
         │
         ├─ unet.load_param(paramfn)   // 加载网络结构
         ├─ unet.load_model(binfn)     // 加载权重
         └─ 加载 mask 权重文件

┌─────────────────────────────────────────────────────────────┐
│                  3. 音频模型加载阶段                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: scrfdncnn.initWenet(wenetfn)
                              │
                              ▼
    创建 WeNet 音频特征提取模型（ONNX）

┌─────────────────────────────────────────────────────────────┐
│                    4. 会话管理阶段                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: long sessid = scrfdncnn.newsession()
                              │
                              ▼
    创建新的处理会话，管理音频流

┌─────────────────────────────────────────────────────────────┐
│                    5. 音频数据处理                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: scrfdncnn.pushpcm(sessid, data, size, 0)
                              │
                              ▼
    推送 PCM 音频数据到会话
                              │
                              ▼
    后台线程自动进行 WeNet 特征提取

┌─────────────────────────────────────────────────────────────┐
│                  6. 图像推理阶段                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: scrfdncnn.filerst(sessid, picfile, maskfile, box, ...)
                              │
                              ▼
    JNI: Java_ai_guiji_duix_DuixNcnn_filerst()
                              │
                              ▼
    C++: dhduix_fileinx()
         │
         ├─ 加载图像文件（JPG）
         ├─ 加载 mask 文件
         │
         ▼
    dhduix_simpinx()
         │
         ├─ 读取对应帧的 WeNet 特征
         │
         ▼
    dhduix_simprst()
         │
         ├─ 创建 JMat 对象包装数据
         ├─ 创建 MWorkMat 预处理对象
         │
         ▼
    Mobunet::domodel()
         │
         ├─ 图像预处理（归一化）
         ├─ 合并 6 通道输入
         ├─ 准备音频特征
         ├─ 创建 ncnn::Extractor
         ├─ 设置输入张量
         ├─ 执行推理 extract()
         ├─ 后处理（反归一化）
         └─ Alpha 混合
                              │
                              ▼
    返回处理后的图像数据到 Java 层

┌─────────────────────────────────────────────────────────────┐
│                    7. 清理阶段                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    Java: scrfdncnn.free(0)
                              │
                              ▼
    释放所有资源
```

### Java 层使用示例 - `RenderThread.java`

```java
// 1. 初始化
scrfdncnn = new DuixNcnn();
ModelInfo info = ModelInfoLoader.load(mContext, scrfdncnn, 
                                      duixDir + "/model/gj_dh_res", 
                                      modelDir.getAbsolutePath());

// 2. 分配资源
scrfdncnn.alloc(0, 20, info.getWidth(), info.getHeight());

// 3. 初始化模型
scrfdncnn.initPcmex(0, 10, 20, 50, 0);
if (info.getModelkind() > 0) {
    scrfdncnn.initMunetex(info.getUnetparam(), info.getUnetbin(), 
                          info.getUnetmsk(), info.getModelkind());
} else {
    scrfdncnn.initMunet(info.getUnetparam(), info.getUnetbin(), 
                        info.getUnetmsk());
}
scrfdncnn.initWenet(info.getWenetfn());

// 4. 创建会话
long sessionId = scrfdncnn.newsession();

// 5. 推送音频数据
scrfdncnn.pushpcm(sessionId, audioData, audioData.length, 0);

// 6. 查询准备好的帧数
int readyCnt = scrfdncnn.readycnt(sessionId);

// 7. 执行推理
if (readyCnt > 0) {
    scrfRst = scrfdncnn.filerst(
        sessionId, 
        frame.sgPath,      // 图像文件路径
        frame.maskPath,    // mask 文件路径
        frame.rect,        // 人脸框
        "", 
        bnfIndex,          // 特征索引
        rawBuffer.array(), // 输出图像
        maskBuffer.array(),// 输出mask
        imgSize
    );
}

// 8. 结束会话
scrfdncnn.finsession(sessionId);

// 9. 释放资源
scrfdncnn.free(0);
```

---

## 关键技术点

### 1. NCNN 配置

```cpp
// 不使用 Vulkan GPU 加速
unet.opt.use_vulkan_compute = false;

// 使用 CPU 大核
unet.opt.num_threads = ncnn::get_big_cpu_count();
```

### 2. 模型文件格式

NCNN 支持两种格式的参数文件：

#### Param 文件（网络结构）
- **`.param` 文件**：**文本格式**，描述网络结构
  - 人类可读，可用文本编辑器打开
  - 示例内容：
    ```
    7767517
    75 83
    Input            data             0 1 data
    Convolution      conv1            1 1 data conv1 0=64 1=3 2=1 3=2 4=1 5=1 6=1728
    BatchNorm        bn1              1 1 conv1 bn1 0=64
    ```
  - 加载方式：`unet.load_param(paramfn)`
  
- **`.param.bin` 文件**：**二进制格式**，描述网络结构
  - 不可读，文件更小，加载更快
  - 加载方式：`unet.load_param_bin(paramfn)`

#### 权重文件
- **`.bin` 文件**：二进制格式，存储模型权重数据
  - 加载方式：`unet.load_model(binfn)`

#### 其他文件
- **`weight_*.bin`**：Alpha 混合权重文件

**本项目使用**：`.param`（文本格式）+ `.bin`（权重）

### 3. 输入输出规格

#### 输入

| 名称    | 类型         | 维度          | 说明                |
|---------|--------------|---------------|---------------------|
| face    | ncnn::Mat    | WxHx6         | 6通道图像（RGB+Mask） |
| audio   | ncnn::Mat    | 256x20x1      | 音频特征（WeNet）    |

#### 输出

| 名称    | 类型         | 维度          | 说明                |
|---------|--------------|---------------|---------------------|
| output  | ncnn::Mat    | WxHx3         | 3通道 RGB 图像       |

### 4. 数据归一化

#### 输入归一化
```cpp
// 像素值从 [0, 255] 映射到 [-1, 1]
mean_vals = {127.5, 127.5, 127.5}
norm_vals = {1/127.5, 1/127.5, 1/127.5}
normalized = (input - 127.5) * (1/127.5)
```

#### 输出反归一化
```cpp
// 从 [-1, 1] 映射回 [0, 255]
outmean_vals = {-1.0, -1.0, -1.0}
outnorm_vals = {127.5, 127.5, 127.5}
output = (normalized - (-1.0)) * 127.5
```

### 5. 多线程处理

```cpp
// 后台线程进行音频特征提取
static void *calcworker(void *arg) {
    dhduix_t* duix = (dhduix_t*)arg;
    while (duix->running) {
        PcmSession* sess = duix->cursess;
        if (sess && (sess->sessid() == duix->sessid)) {
            // 执行 WeNet 特征提取
            rst = sess->runcalc(duix->sessid, duix->weai_common, duix->mincalc);
        }
        jtimer_mssleep(10);
    }
    return NULL;
}
```

### 6. Alpha 混合策略

```cpp
// BlendGramAlpha 函数将推理结果与原图融合
// 使用预加载的权重矩阵控制混合比例
BlendGramAlpha(
    (uchar*)result_data,   // 推理结果
    (uchar*)weights_data,  // 权重矩阵（控制混合程度）
    (uchar*)original_data, // 原始图像
    width, 
    height
);
```

### 7. 性能优化

#### 图像加载优化
```cpp
// 使用 JMat 类直接加载 JPG 到内存
mat_pic->loadjpg(sfnpic, 1);
```

#### 内存管理
```cpp
// 使用内存池和引用计数
mat_weights->forceref(0);  // 强制引用，避免重复分配
```

#### 推理性能监控
```cpp
// 监控推理时间，超过 40ms 记录日志
uint64_t ticka = jtimer_msstamp();
rst = dg->munet->domodel(mpic, mmsk, feat, dg->rect);
uint64_t tickb = jtimer_msstamp();
if ((tickb - ticka) > 40) {
    printf("===domodel dist %ld\n", tickb - ticka);
}
```

### 8. 会话管理

```cpp
// 使用 session ID 管理多个推理流
struct dhduix_s {
    volatile uint64_t sessid;     // 当前会话 ID
    PcmSession* cursess;          // 当前会话
    std::queue<PcmSession*> *slist; // 历史会话队列
    pthread_mutex_t pushmutex;    // 推送锁
    pthread_mutex_t readmutex;    // 读取锁
    pthread_mutex_t freemutex;    // 释放锁
};
```

### 9. CMake 编译配置

```cmake
# 查找 NCNN 库
set(ncnn_DIR ${CMAKE_SOURCE_DIR}/third/ncnn-20231027-android-shared/${ANDROID_ABI}/lib/cmake/ncnn)
find_package(ncnn REQUIRED)

# 链接库
target_link_libraries(gjduix
    dhcore          # 核心工具
    dhmfcc          # 音频处理
    dhunet          # 模型推理
    ${OpenCV_LIBS}  # OpenCV
    ncnn            # NCNN
    onnx-lib        # ONNX Runtime
    libjpeg         # JPEG 解码
    turbojpeg       # TurboJPEG
    -landroid       # Android 系统库
)
```

### 10. 支持的架构

根据 NCNN 库目录结构：
- `arm64-v8a`：64位 ARM 架构
- `armeabi-v7a`：32位 ARM 架构
- `x86`：32位 x86 架构
- `x86_64`：64位 x86 架构

---

## 总结

Duix-Android 的 NCNN 模型推理实现了一个完整的音视频同步数字人系统：

1. **模型加载**：使用 NCNN 加载 `.param` 和 `.bin` 格式的模型文件
2. **数据预处理**：图像归一化到 [-1, 1]，合并真实图和 mask 为 6 通道输入
3. **音频处理**：使用 WeNet 模型提取音频特征，与图像联合推理
4. **模型推理**：双输入（图像+音频）单输出（图像）的 NCNN 推理
5. **后处理**：反归一化并使用 Alpha 混合将结果与原图融合
6. **性能优化**：多线程处理、内存池、性能监控等优化措施

整个系统通过 JNI 层连接 Java 和 C++，实现了高效的实时数字人渲染能力。

