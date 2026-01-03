# DUIX / HeyGen Mobile Model Reverse Engineering

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-2.0+-red.svg" alt="PyTorch">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

> 🔬 DUIX/HeyGen 移动端数字人模型的逆向工程与 PyTorch 复现

---

## 📖 项目简介

本项目对 [DUIX](https://github.com/AixiaoyeYingying/Duix-Mobile)（硅基智能开源的移动端数字人方案）中使用的 **NCNN 神经网络模型**进行了深入分析和 PyTorch 复现。

### 🎯 主要成果

| 成果 | 描述 |
|------|------|
| **模型解密** | 破解 AES-128-CBC 加密的模型文件 |
| **结构分析** | 完整解析 MobileNetV2 + U-Net 架构 |
| **PyTorch 复现** | 95% 结构一致性的 PyTorch 实现 |
| **推理复现** | 音频驱动人脸生成的完整流程 |

### 🔍 发现

- **模型架构**: MobileNetV2 编码器 + U-Net 解码器
- **双输入单输出**: 音频特征 + 6通道人脸图像 → 生成图像
- **加密方式**: AES-128-CBC，密钥硬编码在 JNI 代码中
- **参数量**: ~3.77M（轻量级设计）

---

## 📁 项目结构

```
duix-heygen-reverse/
├── README.md                           # 本文件
├── LICENSE                             # MIT 许可证
├── .gitignore                          # Git 忽略配置
│
├── models/                             # 🧠 模型复现代码
│   ├── MobileNet_Fixed.py              # ✅ PyTorch 复现模型
│   └── README.md                       # 模型使用说明
│
├── tools/                              # 🔧 工具脚本
│   ├── decrypt_model.py                # 模型解密工具
│   └── README.md                       # 工具使用说明
│
├── docs/                               # 📚 技术文档
│   ├── encryption_analysis.md          # 加密机制分析
│   ├── model_structure_analysis.md     # 模型结构分析
│   └── ncnn_inference_analysis.md      # NCNN 推理流程分析
│
└── examples/                           # 💡 使用示例
    ├── inference.py                    # PyTorch 模型推理示例
    └── audio_inference.py              # 音频特征提取推理示例
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install torch torchvision numpy
pip install pycryptodome  # 用于模型解密
pip install onnxruntime librosa soundfile  # 用于音频特征提取
```

### 基础使用

```python
from models.MobileNet_Fixed import MobileNetV2Unet
import torch

# 创建模型
model = MobileNetV2Unet(use_groupnorm=False)
model.eval()

# 准备输入
audio = torch.randn(1, 256, 20)      # 音频特征 [B, 256, 20]
face = torch.randn(1, 6, 160, 160)   # 6通道人脸 [B, 6, H, W]

# 推理
with torch.no_grad():
    output = model(face, audio)       # [B, 3, 160, 160]

print(f"输出形状: {output.shape}")    # torch.Size([1, 3, 160, 160])
print(f"输出范围: [{output.min():.2f}, {output.max():.2f}]")  # [-1, 1]
```

### 解密模型文件

```bash
# 解密 NCNN 模型文件
python tools/decrypt_model.py path/to/dh_model.p decrypted_model.param
python tools/decrypt_model.py path/to/dh_model.b decrypted_model.bin

# 解密 WeNet ONNX 模型文件
python tools/decrypt_wenet.py path/to/encrypted_wenet.onnx wenet.onnx
```

### 音频特征提取

```bash
# 使用解密后的 WeNet 模型提取音频特征
python examples/audio_inference.py wenet.onnx audio.wav output_bnf.npy
```

---

## 🏗️ 模型架构

### 整体结构

```
输入
├── Audio:  [B, 256, 20]    # 音频特征（如 Wenet 提取）
└── Face:   [B, 6, 160, 160] # 当前帧 + 参考帧（各3通道）
      │
      ▼
┌─────────────────────────────────────────────┐
│            Audio Encoder (8层)               │
│     [B, 256, 20] ──────► [B, 128, 5, 5]     │
└─────────────────────────────────────────────┘
      │
      │                ┌─────────────────────────────────────────────┐
      │                │         Image Encoder (MobileNetV2)         │
      │                │                                             │
      │                │  [B, 6, 160, 160]                           │
      │                │        │                                    │
      │                │        ▼                                    │
      │                │  ┌──► x1: [B, 16, 80, 80]  ─────────┐      │
      │                │  │                                   │      │
      │                │  ├──► x2: [B, 24, 40, 40]  ────────┐│      │
      │                │  │                                 ││      │
      │                │  ├──► x3: [B, 32, 20, 20]  ───────┐││      │
      │                │  │                                │││      │
      │                │  ├──► x4: [B, 96, 10, 10]  ──────┐│││      │
      │                │  │                               ││││      │
      │                │  └──► x5: [B, 320, 5, 5]  ──────┐││││      │
      │                │                                 │││││      │
      │                └─────────────────────────────────┼┼┼┼┼──────┘
      │                                                  │││││
      ▼                                                  ▼▼▼▼▼
┌─────────────────────────────────────────────────────────────────────┐
│                    U-Net Decoder (跳跃连接)                          │
│                                                                      │
│  [audio + x5] ──► [96, 5, 5]                                        │
│       │                                                              │
│       ▼ + x4                                                         │
│  [96, 10, 10] ──► [96, 10, 10]                                      │
│       │                                                              │
│       ▼ + x3                                                         │
│  [32, 20, 20] ──► [32, 20, 20]                                      │
│       │                                                              │
│       ▼ + x2                                                         │
│  [24, 40, 40] ──► [24, 40, 40]                                      │
│       │                                                              │
│       ▼ + x1                                                         │
│  [16, 80, 80] ──► [16, 80, 80]                                      │
│       │                                                              │
│       ▼                                                              │
│  [8, 160, 160] ──► Conv ──► TanH ──► [3, 160, 160]                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
输出: [B, 3, 160, 160]  # 生成的 RGB 图像，范围 [-1, 1]
```

### 关键设计

| 组件 | 设计 | 参数量 |
|------|------|--------|
| Audio Encoder | 8层 Conv + Residual | ~0.55M |
| Image Encoder | MobileNetV2 Backbone | ~1.92M |
| U-Net Decoder | 5级跳跃连接 + InvertedResidual | ~2.06M |
| **总计** | - | **~4.53M** |

---

## 🔐 加密分析

### 加密方式

| 项目 | 值 |
|------|-----|
| **算法** | AES-128-CBC |
| **密钥** | `yymrjzbwyrbjszrk` (16字节) |
| **IV** | `yymrjzbwyrbjszrk` (16字节) |
| **文件头** | `gjdigits` (8字节魔数) |

### 加密文件

| 文件 | 内容 |
|------|------|
| `dh_model.p` | 网络结构 (.param) |
| `dh_model.b` | 模型权重 (.bin) |
| `config.j` | 配置文件 |
| `bbox.j` | 边界框配置 |
| `wenet.onnx` | WeNet 音频特征提取模型（ONNX 格式） |

### 解密方法

密钥直接硬编码在 Android JNI 代码中：

```c
// duix-sdk/src/main/cpp/aes/aesmain.c
char* key = "yymrjzbwyrbjszrk";
char* aiv = "yymrjzbwyrbjszrk";
```

详见 [加密分析文档](docs/encryption_analysis.md)。

---

## 📊 与原版对比

### 结构一致性

| 项目 | NCNN 原版 | PyTorch 复现 | 状态 |
|------|-----------|--------------|------|
| 输入形状 | audio(256×20) + face(6×H×W) | ✅ 相同 | ✅ |
| 输出形状 | 3×H×W | ✅ 相同 | ✅ |
| 输出激活 | TanH [-1, 1] | ✅ TanH [-1, 1] | ✅ |
| 参数量 | 3.77M | 4.53M (+20%) | ⚠️ |
| 归一化 | GroupNorm | BatchNorm (可选) | ⚠️ |
| 结构一致性 | 100% | ~95% | ✅ |

### 参数量差异原因

- 解码器使用 `expand_ratio=6` 的 InvertedResidual
- 可通过调整 `expand_ratio` 降低参数量

---

## 📚 文档

| 文档 | 描述 |
|------|------|
| [模型结构分析](docs/model_structure_analysis.md) | NCNN 模型逐层解析 |
| [加密机制分析](docs/encryption_analysis.md) | AES 加密破解过程 |
| [推理流程分析](docs/ncnn_inference_analysis.md) | NCNN 推理代码分析 |
| [音频特征提取](docs/audio_feature_extraction.md) | WeNet ONNX 音频特征提取 |

---

## ⚠️ 免责声明

本项目仅用于**学习和研究目的**。

- 📖 所有分析基于公开的开源代码
- 🔬 旨在理解移动端数字人技术的实现
- ⚖️ 请遵守相关法律法规和开源协议
- 🚫 请勿用于商业目的或侵犯他人权益

---

## 🙏 致谢

- [DUIX / 硅基智能](https://github.com/AixiaoyeYingying/Duix-Mobile) - 开源的移动端数字人方案
- [NCNN](https://github.com/Tencent/ncnn) - 腾讯的高性能神经网络推理框架
- [MobileNetV2](https://arxiv.org/abs/1801.04381) - 轻量级骨干网络

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 可以做的事情

- [x] 完善权重转换脚本（NCNN → PyTorch）
- [x] 添加音频特征提取推理示例
- [x] 添加 WeNet ONNX 模型解密工具
- [ ] 优化参数量到与原版一致
- [ ] 添加训练代码
- [ ] 添加完整的端到端推理流程示例

---

<p align="center">
  <b>⭐ 如果这个项目对你有帮助，请给个 Star！</b>
</p>

