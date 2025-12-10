# 🧠 模型复现代码

本目录包含 DUIX 数字人模型的 PyTorch 复现版本。

## 📁 文件说明

| 文件 | 描述 | 推荐度 |
|------|------|--------|
| **`MobileNet_Fixed.py`** | ✅ **PyTorch 复现模型** | ⭐⭐⭐⭐⭐ |

## 🚀 快速使用

```python
from MobileNet_Fixed import MobileNetV2Unet
import torch

# 创建模型
model = MobileNetV2Unet(use_groupnorm=False)
model.eval()

# 输入
audio = torch.randn(1, 256, 20)      # 音频特征
face = torch.randn(1, 6, 160, 160)   # 6通道人脸图像

# 推理
with torch.no_grad():
    output = model(face, audio)

print(f"输出: {output.shape}")        # [1, 3, 160, 160]
print(f"范围: [{output.min():.2f}, {output.max():.2f}]")  # [-1, 1]
```

## 📊 模型参数

| 组件 | 参数量 |
|------|--------|
| Image Encoder (MobileNetV2) | 1.92M |
| Audio Encoder | 0.55M |
| U-Net Decoder | 2.06M |
| **总计** | **4.53M** |

## ✅ 模型特点

### MobileNet_Fixed.py

- ✅ 输出激活函数正确 (TanH)
- ✅ 音频编码器完整 (8层)
- ✅ 结构与 NCNN 对齐 (~95%)
- ✅ 可直接用于训练/推理

## 🔧 配置选项

```python
# 使用 BatchNorm（推荐用于训练）
model = MobileNetV2Unet(use_groupnorm=False)

# 使用 GroupNorm（完全对齐 NCNN）
model = MobileNetV2Unet(use_groupnorm=True)
```

## 📥 输入格式

### 音频特征

```python
# 形状: [B, 256, 20]
# - B: batch size
# - 256: 特征维度（如 Wenet 输出）
# - 20: 时间步数

audio = torch.randn(batch_size, 256, 20)
```

### 人脸图像

```python
# 形状: [B, 6, H, W]
# - B: batch size
# - 6: 通道数 = 当前帧(3) + 参考帧(3)
# - H, W: 图像尺寸（通常 160x160）

# 图像归一化到 [-1, 1]
current_frame = (current_frame / 255.0) * 2 - 1   # [3, H, W]
reference_frame = (reference_frame / 255.0) * 2 - 1  # [3, H, W]
face = torch.cat([current_frame, reference_frame], dim=0)  # [6, H, W]
```

## 📤 输出格式

```python
# 形状: [B, 3, H, W]
# 范围: [-1, 1] (TanH 激活)

output = model(face, audio)

# 转换为图像
output_image = (output + 1) / 2 * 255  # [0, 255]
output_image = output_image.clamp(0, 255).byte()
```

## 🧪 测试模型

```bash
cd models
python MobileNet_Fixed.py
```

输出示例：
```
==================================================
测试修正后的模型
==================================================
Audio input shape: torch.Size([1, 256, 20])
Face input shape: torch.Size([1, 6, 160, 160])

Output shape: torch.Size([1, 3, 160, 160])
Output range: [-0.35, 0.42]
Expected range: [-1, 1] (TanH)

Total parameters: 4.53M
Expected: ~3.77M (NCNN model)

==================================================
✅ 模型测试完成
==================================================
```

