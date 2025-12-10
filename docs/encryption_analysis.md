# Duix-Mobile 模型文件加密与解密分析

## 📋 目录

1. [模型文件概述](#模型文件概述)
2. [加密方式分析](#加密方式分析)
3. [文件格式详解](#文件格式详解)
4. [解密实现](#解密实现)
5. [模型结构分析](#模型结构分析)
6. [代码加载流程](#代码加载流程)

---

## 模型文件概述

### Kai 目录文件列表

```
Kai/
├── dh_model.p (15KB)          # 加密的 NCNN 模型结构文件
├── dh_model.b (14MB)          # 加密的 NCNN 模型权重文件
├── config.j (160B)            # 加密的配置文件
├── bbox.j (14KB)              # 加密的人脸框坐标文件
├── weight_168u.bin (25KB)     # Alpha 混合权重（未加密）
└── raw_jpgs/                  # 视频帧图像目录
    ├── 1.sij ~ 501.sij        # 501 帧图像（JPEG 格式，虽然扩展名是 .sij）
```

### 文件用途

| 文件名 | 真实格式 | 是否加密 | 用途 |
|--------|----------|----------|------|
| dh_model.p | NCNN .param (文本) | ✅ 是 | 模型网络结构定义 |
| dh_model.b | NCNN .bin (二进制) | ✅ 是 | 模型权重数据 |
| config.j | JSON | ✅ 是 | 模型配置（分辨率等） |
| bbox.j | JSON | ✅ 是 | 每一帧的人脸框坐标 |
| weight_168u.bin | Binary | ❌ 否 | Alpha 混合权重矩阵 |
| *.sij | JPEG | ❌ 否 | 视频帧图像（标准 JPEG） |

---

## 加密方式分析

### 1️⃣ 加密算法

**AES-128-CBC** (Advanced Encryption Standard, 128-bit, Cipher Block Chaining)

### 2️⃣ 加密密钥

```c
// 在 aesmain.c 中明文硬编码
char* key = "yymrjzbwyrbjszrk";  // 16字节密钥
char* aiv = "yymrjzbwyrbjszrk";  // 16字节初始化向量(IV)
```

⚠️ **安全风险**：密钥在代码中明文硬编码，容易被逆向获取。

### 3️⃣ 文件格式

```
+------------------+------------------+------------------+------------------+
| 魔数 (8 bytes)   | 原始大小 (8 bytes)| 保留 (16 bytes)  | 加密数据 (变长)   |
+------------------+------------------+------------------+------------------+
| "gjdigits"       | uint64_t size    | (padding)        | AES encrypted    |
+------------------+------------------+------------------+------------------+
```

**头部结构**（32 字节）：
- **Offset 0-7**: 魔数 `gjdigits` (8字节)
- **Offset 8-15**: 原始文件大小 (uint64_t, 小端序)
- **Offset 16-31**: 保留字段（通常为0）

**加密数据**：
- 从第 32 字节开始
- 使用 AES-128-CBC 加密
- 按 16 字节块加密
- 最后一块使用零填充

### 4️⃣ 加密/解密代码位置

```cpp
// 加密/解密实现
duix-android/dh_aigc_android/duix-sdk/src/main/cpp/aes/aesmain.c
    → mainenc(int enc, char* infn, char* outfn)
    
// AES 核心算法
duix-android/dh_aigc_android/duix-sdk/src/main/cpp/aes/gj_aes.c
    → init_aesc()
    → do_aesc()

// JNI 接口
duix-android/dh_aigc_android/duix-sdk/src/main/cpp/android/DuixJni.cpp
    → Java_ai_guiji_duix_DuixNcnn_processmd5()
```

---

## 文件格式详解

### 1. dh_model.p (NCNN Param 文件)

**解密后格式**：文本文件，NCNN 标准 param 格式

```
7767517                          ← NCNN 魔数
165 181                          ← 层数 输入/输出数
Input                    audio                      0 1 audio
Input                    face                       0 1 face
Convolution              convrelu_0               1 1 audio 2 0=16 1=3 ...
...
```

**文件头部信息**：
- 魔数：`7767517` (NCNN 格式标识)
- 层数：165 层
- 输入/输出数：181

**关键信息**：
- **双输入**：`audio` (音频特征) 和 `face` (6通道图像)
- **单输出**：`output` (3通道生成图像)
- **模型类型**：基于 MobileNet 的 U-Net 架构
- **原始大小**：15,730 字节

### 2. dh_model.b (NCNN Bin 文件)

**解密后格式**：二进制权重文件

```
文件头部（十六进制）:
476b3001 2f422541 40c002c3 0c4544c2 d43a81c7 5cbda5bc ...
```

**文件信息**：
- **原始大小**：15,078,184 字节 (约 14.4 MB)
- **内容**：模型的所有权重参数（浮点数）
- **加密前魔数**：`Gk0` + 二进制数据

### 3. config.j (配置文件)

**解密后格式**：JSON

```json
{
    "width": 540, 
    "height": 960, 
    "need_png": 1, 
    "res_fmt": "sij", 
    "ranges": null, 
    "reverse": null, 
    "removegreen": true
}
```

**配置说明**：
- `width/height`: 视频分辨率 540×960
- `res_fmt`: 资源格式为 "sij"
- `removegreen`: 需要去除绿幕

### 4. bbox.j (人脸框文件)

**解密后格式**：JSON (每帧的人脸框坐标)

```json
{
    "1": [117, 395, 358, 636],      ← 第1帧：[x1, y1, x2, y2]
    "2": [117, 395, 358, 636],
    "3": [117, 395, 357, 635],
    ...
    "501": [117, 394, 357, 634]
}
```

**坐标说明**：
- 格式：`[x1, y1, x2, y2]` (左上角和右下角坐标)
- 共 501 帧
- 人脸框大小：约 241×241 像素
- 位置相对稳定（说话时头部轻微移动）

### 5. *.sij 文件（图像文件）

**实际格式**：标准 JPEG 图像（未加密）

```
文件头部（十六进制）:
ffd8 ffe0 0010 4a46 4946 0001 0100 0001 ...
       ↑
    JPEG 魔数 (FFD8)，JFIF 格式
```

**文件信息**：
- **真实格式**：JPEG
- **扩展名**：.sij (可能是 "Simple Image JPEG" 的缩写)
- **是否加密**：❌ 否（可以直接用图片查看器打开）
- **数量**：501 张图片（对应 501 帧）

---

## 解密实现

### Python 解密脚本

```python
#!/usr/bin/env python3
import struct
from Crypto.Cipher import AES

# 硬编码的密钥和 IV
key = b"yymrjzbwyrbjszrk"
iv = b"yymrjzbwyrbjszrk"

def decrypt_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        # 1. 读取并验证魔数
        magic = f.read(8)
        if magic != b'gjdigits':
            print(f"错误：不是有效的加密文件")
            return False
        
        # 2. 读取原始文件大小
        real_size = struct.unpack('<Q', f.read(8))[0]
        
        # 3. 跳过保留字段
        f.read(16)
        
        # 4. 读取加密数据
        encrypted_data = f.read()
        
        # 5. AES-128-CBC 解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 6. 截取实际大小（去除填充）
        decrypted_data = decrypted_data[:real_size]
        
        # 7. 写入解密后的文件
        with open(output_file, 'wb') as out:
            out.write(decrypted_data)
        
        print(f"解密成功！原始大小: {real_size} bytes")
        return True

# 使用示例
decrypt_file('Kai/dh_model.p', 'dh_model.param')
decrypt_file('Kai/dh_model.b', 'dh_model.bin')
decrypt_file('Kai/config.j', 'config.json')
decrypt_file('Kai/bbox.j', 'bbox.json')
```

### C/C++ 解密代码（项目中的实现）

```cpp
// aes/aesmain.c
int mainenc(int enc, char* infn, char* outfn) {
    char* key = "yymrjzbwyrbjszrk";
    char* aiv = "yymrjzbwyrbjszrk";
    
    FILE* fr = fopen(infn, "rb");
    FILE* fw = fopen(outfn, "wb");
    
    gj_aesc_t* aesc = NULL;
    init_aesc(key, aiv, enc, &aesc);  // enc: 0=解密, 1=加密
    
    if (enc) {
        // 加密模式
        fwrite("gjdigits", 1, 8, fw);       // 写入魔数
        uint64_t size = 0;
        fwrite(&size, 1, 8, fw);            // 占位符
        fwrite(&size, 1, 8, fw);
        fwrite(&size, 1, 8, fw);
        
        // 按 16 字节块加密
        while (!feof(fr)) {
            char data[16];
            memset(data, 0, 16);
            uint64_t rst = fread(data, 1, 16, fr);
            if (rst) {
                size += rst;
                do_aesc(aesc, data, 16, result, &outlen);
                fwrite(result, 1, outlen, fw);
            }
        }
        
        // 回写真实大小
        fseek(fw, 8, 0);
        fwrite(&size, 1, 8, fw);
    } else {
        // 解密模式
        char result[255];
        uint64_t rst = fread(result, 1, 32, fr);  // 读取头部
        
        // 验证魔数
        if ((result[0] != 'g') || (result[1] != 'j')) {
            return -1004;  // 无效文件
        }
        
        uint64_t* psize = (uint64_t*)(result + 8);
        uint64_t realsize = *psize;
        
        // 按 16 字节块解密
        while (!feof(fr)) {
            char data[16];
            memset(data, 0, 16);
            uint64_t rst = fread(data, 1, 16, fr);
            if (rst) {
                size += rst;
                do_aesc(aesc, data, 16, result, &outlen);
                
                // 处理最后一块的填充
                if (size > realsize) {
                    outlen -= (size - realsize);
                }
                fwrite(result, 1, outlen, fw);
            }
        }
    }
    
    fclose(fr);
    fclose(fw);
    return 0;
}
```

### 流式解密（用于模型加载）

```cpp
// aes/gaes_stream.cc
class GaesIStreamBuf : public std::streambuf {
    gj_aesc_t* aesc;
    FILE* file;
    uint64_t cur_size;
    uint64_t file_size;
    
public:
    GaesIStreamBuf(std::string& filename) {
        file = fopen(filename.c_str(), "rb");
        
        // 初始化 AES 解密器
        char* key = "yymrjzbwyrbjszrk";
        char* aiv = "yymrjzbwyrbjszrk";
        init_aesc(key, aiv, 0, &this->aesc);  // 0 = 解密
        
        // 读取并跳过头部
        char head[50];
        fread(head, 1, 8, file);           // 读取魔数
        fread(&cur_size, 1, 8, file);      // 读取文件大小
        fread(head, 1, 16, file);          // 跳过保留字段
        cur_size = 32;
    }
    
    // 重写 underflow() 实现流式解密
    int_type underflow() override {
        // ... 从文件读取加密块，解密后返回 ...
    }
};

// 使用流式解密读取 NCNN 模型
std::string filename = "dh_model.p";
GaesIStream fin(filename);  // 自动解密

// NCNN 直接从解密流读取
ncnn::Net unet;
unet.load_param(fin);  // 无需先解密整个文件
```

---

## 模型结构分析

### 网络架构

**类型**：Audio-Visual Talking Head Generation Model (音视频驱动的说话人头像生成模型)

**基础架构**：MobileNetV2 + U-Net

### 输入/输出

#### 输入

| 名称 | 维度 | 说明 |
|------|------|------|
| `audio` | 256×20×1 | 音频特征（WeNet 提取的 BNF 特征）|
| `face` | W×H×6 | 6通道图像（3通道真实图 + 3通道mask）|

#### 输出

| 名称 | 维度 | 说明 |
|------|------|------|
| `output` | W×H×3 | 3通道 RGB 图像（生成的说话人脸）|

### 网络层统计

```
总层数: 165 层
输入/输出节点数: 181

层类型分布:
- Input: 2               (输入层)
- Convolution: 53        (卷积层)
- ConvolutionDepthWise: 22  (深度可分离卷积)
- Deconvolution: 6       (反卷积/上采样)
- GroupNorm: 15          (组归一化)
- ReLU: 61               (激活函数)
- BinaryOp: 7            (二元运算，如 Add)
- Split: 13              (张量分割)
- Concat: 5              (张量拼接)
- Padding: 2             (填充)
- TanH: 1                (输出激活)
```

### 关键网络组件

#### 1. 音频编码器

```
Input(audio) → 
Convolution(16, k3, s2) → ReLU →
Convolution(32, k3, s2) → ReLU →
Convolution(32, k3, s1) + Residual →
Convolution(64, k3, s2) → ReLU →
Convolution(128, k3, s2) → ReLU →
Convolution(128, k3, dilation=2, s2) → ReLU →
Convolution(128, k3, dilation=2, s2) + Residual →
... (提取音频特征向量)
```

#### 2. 图像编码器（MobileNetV2）

```
Input(face, 6 channels) → Padding →
Convolution(16, k3) → ReLU →
Convolution(32, k3, s2) → ReLU →

[Inverted Residual Block] ×N:
  → Expansion Conv(1×1) → ReLU
  → DepthWise Conv(3×3) → ReLU
  → Projection Conv(1×1)
  → GroupNorm → ReLU
  + Skip Connection

... (逐步下采样，提取图像特征)
```

#### 3. 特征融合与解码器（U-Net）

```
[多尺度特征融合]:
  Audio Features + Image Features → Concat

[解码器]:
  → Deconvolution(上采样) ×5
  → Concat(with encoder features, skip connection)
  → Convolution blocks
  → GroupNorm → ReLU

[输出层]:
  → Padding
  → Convolution(3, k3) → TanH
  → Output(3 channels, RGB image)
```

### 模型特点

1. **轻量级设计**：
   - 使用 MobileNetV2 深度可分离卷积
   - 模型大小仅 ~14MB
   - 适合移动端部署

2. **多模态融合**：
   - 音频编码器：提取语音的声学特征
   - 图像编码器：提取人脸的视觉特征
   - 融合后生成同步的说话动作

3. **U-Net 结构**：
   - 编码器：逐步下采样提取特征
   - 解码器：逐步上采样恢复分辨率
   - 跳跃连接：保留细节信息

4. **归一化策略**：
   - 使用 GroupNorm 而非 BatchNorm
   - 更适合小批量推理

5. **输出激活**：
   - TanH 激活函数，输出范围 [-1, 1]
   - 需要反归一化到 [0, 255]

### 模型参数量估算

```python
# 主要卷积层参数量:
# Convolution: out_channels × in_channels × kernel_h × kernel_w
# DepthWise: channels × kernel_h × kernel_w

总参数量 ≈ 15,078,184 bytes / 4 bytes/float ≈ 3.77M 参数
```

---

## 代码加载流程

### 1. Java 层调用

```java
// RenderThread.java
ModelInfo info = ModelInfoLoader.load(
    mContext, 
    scrfdncnn, 
    duixDir + "/model/gj_dh_res",  // 基础资源目录
    modelDir.getAbsolutePath()      // 模型目录 (Kai/)
);

// 初始化模型
scrfdncnn.initMunet(
    info.getUnetparam(),  // dh_model.p 的路径
    info.getUnetbin(),    // dh_model.b 的路径
    info.getUnetmsk()     // weight_168u.bin 的路径
);
```

### 2. JNI 层处理

```cpp
// DuixJni.cpp
JNIEXPORT jint JNICALL Java_ai_guiji_duix_DuixNcnn_initMunet(
    JNIEnv *env, jobject thiz,
    jstring fnparam, jstring fnbin, jstring fnmask) {
    
    std::string sparam = getStringUTF(env, fnparam);
    std::string sbin = getStringUTF(env, fnbin);
    std::string smask = getStringUTF(env, fnmask);
    
    // 调用 C++ 层初始化
    int rst = dhduix_initMunet(
        g_digit,
        (char*)sparam.c_str(),
        (char*)sbin.c_str(),
        (char*)smask.c_str()
    );
    
    return rst;
}
```

### 3. C++ 模型加载

```cpp
// munet.cpp
int Mobunet::initModel(const char* binfn, const char* paramfn, const char* mskfn) {
    unet.clear();
    
    // 配置 NCNN
    unet.opt.use_vulkan_compute = false;
    unet.opt.num_threads = ncnn::get_big_cpu_count();
    
    // 关键：这里 NCNN 会自动检测文件是否加密
    // 如果文件头是 "gjdigits"，则使用流式解密读取
    unet.load_param(paramfn);  // 加载 dh_model.p (自动解密)
    unet.load_model(binfn);    // 加载 dh_model.b (自动解密)
    
    // 加载 alpha 混合权重（未加密）
    char* wbuf = NULL;
    dumpfile((char*)mskfn, &wbuf);
    mat_weights = new JMat(160, 160, (uint8_t*)wbuf, 1);
    
    return 0;
}
```

### 4. NCNN 内部加密文件处理

NCNN 本身不支持加密文件，但项目通过**修改 NCNN 源码**或使用**自定义 DataReader** 实现：

#### 方法 A：修改 NCNN 源码

```cpp
// 可能在 ncnn/src/net.cpp 中添加了加密检测
int Net::load_param(const char* protopath) {
    FILE* fp = fopen(protopath, "rb");
    
    // 检查文件头
    char magic[8];
    fread(magic, 1, 8, fp);
    
    if (memcmp(magic, "gjdigits", 8) == 0) {
        // 加密文件，使用解密流
        fclose(fp);
        std::string filename(protopath);
        GaesIStream stream(filename);
        return load_param(stream);
    } else {
        // 普通文件
        fseek(fp, 0, SEEK_SET);
        return load_param(fp);
    }
}
```

#### 方法 B：使用自定义 DataReader

```cpp
// 创建自定义 DataReader
class EncryptedDataReader : public ncnn::DataReader {
    GaesIStream* stream;
public:
    EncryptedDataReader(const std::string& path) {
        stream = new GaesIStream(path);
    }
    
    virtual int scan(const char* format, void* p) const {
        return fscanf(stream, format, p);
    }
    
    virtual int read(void* buf, int size) const {
        return stream->read(buf, size);
    }
};

// 使用自定义 DataReader
EncryptedDataReader reader("dh_model.p");
unet.load_param(reader);
```

### 5. 完整加载流程图

```
┌────────────────────────────────────────────────────────────────┐
│ 1. Java层: ModelInfoLoader.load()                              │
│    → 读取 config.j (加密)                                       │
│    → 解密得到配置信息                                           │
│    → 返回文件路径：dh_model.p, dh_model.b, weight_168u.bin    │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 2. Java层: DuixNcnn.initMunet(param, bin, mask)               │
│    → 通过 JNI 调用 Native 方法                                 │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 3. JNI层: Java_ai_guiji_duix_DuixNcnn_initMunet()             │
│    → 转换 jstring 为 C++ string                                │
│    → 调用 dhduix_initMunet()                                   │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 4. C++层: dhduix_initMunet()                                   │
│    → 创建 Mobunet 对象                                         │
│    → 调用 Mobunet::initModel()                                 │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 5. C++层: Mobunet::initModel()                                 │
│    ├─ unet.load_param(paramfn)  ← dh_model.p                  │
│    │   └→ 检测 "gjdigits" 魔数                                 │
│    │       └→ 使用 GaesIStream 流式解密读取                    │
│    │           └→ AES-128-CBC 解密                              │
│    │               └→ NCNN 解析 param 文本                      │
│    │                                                            │
│    ├─ unet.load_model(binfn)    ← dh_model.b                  │
│    │   └→ 检测 "gjdigits" 魔数                                 │
│    │       └→ 使用 GaesIStream 流式解密读取                    │
│    │           └→ AES-128-CBC 解密                              │
│    │               └→ NCNN 加载权重到内存                       │
│    │                                                            │
│    └─ dumpfile(mskfn)           ← weight_168u.bin             │
│        └→ 直接读取（未加密）                                    │
│            └→ 创建 Alpha 混合权重矩阵                          │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 6. 模型就绪，可以进行推理                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## 总结

### ✅ 模型是否加密？

**是的，模型文件使用 AES-128-CBC 加密。**

加密文件：
- ✅ `dh_model.p` (NCNN param)
- ✅ `dh_model.b` (NCNN bin)
- ✅ `config.j` (配置)
- ✅ `bbox.j` (人脸框)

未加密文件：
- ❌ `weight_168u.bin` (Alpha 权重)
- ❌ `*.sij` (JPEG 图像)

### 🔓 能否解密？

**可以！** 密钥在代码中明文硬编码：
```c
key = "yymrjzbwyrbjszrk"
iv  = "yymrjzbwyrbjszrk"
```

所有加密文件都可以轻松解密。

### 📊 模型结构能否推出？

**完全可以！** 解密 `dh_model.p` 后得到完整的 NCNN param 文件，包含：
- ✅ 完整的网络层定义
- ✅ 所有层的参数配置
- ✅ 输入输出节点信息
- ✅ 层与层之间的连接关系

### 🔑 密钥位置

```cpp
// 密钥硬编码位置：
duix-android/dh_aigc_android/duix-sdk/src/main/cpp/aes/aesmain.c:11
duix-android/dh_aigc_android/duix-sdk/src/main/cpp/aes/gaes_stream.cc:100
```

### ⚠️ 安全性评估

| 安全措施 | 评分 | 说明 |
|----------|------|------|
| 加密算法 | ⭐⭐⭐⭐ | AES-128-CBC，算法本身安全 |
| 密钥管理 | ⭐ | 密钥硬编码在代码中，容易被逆向 |
| 文件格式 | ⭐⭐ | 自定义格式，有一定混淆作用 |
| 整体安全性 | ⭐⭐ | **低**，密钥泄露导致加密形同虚设 |

### 💡 改进建议

1. **密钥管理**：
   - 使用密钥派生函数（PBKDF2, scrypt）
   - 密钥存储在安全硬件（TEE, SE）
   - 动态密钥生成

2. **混淆保护**：
   - 代码混淆
   - 字符串加密
   - Native 代码保护

3. **完整性校验**：
   - 添加 HMAC 校验
   - 防止文件篡改

4. **多层防护**：
   - 文件加密 + 代码混淆 + 反调试
   - 服务端验证

### 📈 模型信息总结

```
模型名称: Audio-Visual Talking Head Generation
模型类型: MobileNetV2 + U-Net
模型大小: ~14.4 MB (权重)
层数: 165 层
参数量: ~3.77M
输入: 
  - audio: 256×20×1 (音频特征)
  - face: W×H×6 (6通道图像)
输出:
  - output: W×H×3 (生成的说话人脸)
分辨率: 540×960
帧数: 501 帧
加密: AES-128-CBC (密钥泄露)
```

---

## 附录

### A. 解密工具使用

```bash
# 解密所有模型文件
python3 decrypt_model.py Kai/dh_model.p dh_model.param
python3 decrypt_model.py Kai/dh_model.b dh_model.bin
python3 decrypt_model.py Kai/config.j config.json
python3 decrypt_model.py Kai/bbox.j bbox.json

# 重命名 .sij 为 .jpg（它们本来就是 JPEG）
for i in Kai/raw_jpgs/*.sij; do
    cp "$i" "${i%.sij}.jpg"
done
```

### B. NCNN 模型可视化

解密后可以使用 NCNN 工具查看模型结构：

```bash
# 使用 netron 可视化
pip install netron
netron dh_model.param

# 或者使用 NCNN 官方工具
./ncnn2table dh_model.param dh_model.bin > model_info.txt
```

### C. 相关文件路径

```
duix-android/dh_aigc_android/duix-sdk/src/main/cpp/
├── aes/
│   ├── aesmain.c           # 加密/解密主函数
│   ├── aesmain.h           # 接口定义
│   ├── gj_aes.c            # AES 算法实现
│   └── gaes_stream.cc      # 流式解密
├── android/
│   └── DuixJni.cpp         # JNI 接口
├── dhunet/
│   ├── munet.cpp           # 模型加载与推理
│   └── munet.h             # 模型类定义
└── duix/
    └── gjsimp.cpp          # 主要推理逻辑
```

