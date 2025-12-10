# MobileNet.py vs NCNN 模型结构对比分析

## 📊 总体对比

| 项目 | NCNN 模型（实际） | PyTorch 复现 | 状态 |
|------|------------------|--------------|------|
| 总层数 | 165 层 | ~类似 | ⚠️ 需验证 |
| 输入 | audio(256×20×1) + face(W×H×6) | audio(256×20) + face(W×H×6) | ✅ 匹配 |
| 输出 | W×H×3 (TanH) | W×H×3 (Sigmoid) | ❌ **激活函数不同** |
| 归一化 | GroupNorm | InstanceNorm2d/BatchNorm2d | ❌ **类型不同** |

---

## 🎵 音频编码器对比

### NCNN 实际结构

```
Input: audio [1, 256, 20]

1. Conv(1→16, k3, s2, p0)           0=16 1=3 2=1 3=2 4=0
   → ReLU
   → [16, 128, 10]

2. Conv(16→32, k3, s2, p0)          0=32 1=3 2=1 3=2 4=0
   → ReLU
   → [32, 64, 5]

3. Conv(32→32, k3, s1, p1)          0=32 1=3 2=1 3=1 4=1
   + Residual (Split + Add)
   → ReLU
   → [32, 64, 5]

4. Conv(32→64, k3, s2, p1)          0=64 1=3 2=1 3=2 4=1
   → ReLU
   → [64, 32, 3]

5. Conv(64→128, k3, s2, p1)         0=128 1=3 2=1 3=2 4=1
   → ReLU
   → [128, 16, 2]

6. Conv(128→128, k3, s2, p1, dilation=2)    13=2 (dilation)
   → ReLU
   → [128, 8, 1]

7. Conv(128→128, k3, s2, p2, dilation=2)    13=2 14=2 (dilation, pad)
   → ReLU
   → [128, 4, 1]

8. Conv(128→128, k3, s1, p1)        0=128 1=3 2=1 3=1 4=1
   + Residual
   → ReLU
   → [128, 4, 1]

最终输出: [128, 4, 1] 或经过进一步处理
```

### PyTorch 复现结构

```python
self.audio_encoder = nn.Sequential(
    Conv2d(1, 32, kernel_size=3, stride=2, padding=1),         # [B, 32, 128, 10]  ❌ 缺少 1→16→32
    Conv2d(32, 32, kernel_size=3, stride=1, padding=1, residual=True),
    
    Conv2d(32, 64, kernel_size=3, stride=2, padding=1),        # [B, 64, 64, 5]
    Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),  # ❌ 多余的层
    
    Conv2d(64, 128, kernel_size=3, stride=2, padding=1),       # [B, 128, 32, 3]
    Conv2d(128, 128, kernel_size=3, stride=2, padding=1),      # [B, 128, 16, 2]
    Conv2d(128, 128, kernel_size=3, stride=2, padding=1),      # [B, 128, 8, 1]  ❌ 缺少 dilation
    Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True),
    
    nn.AdaptiveAvgPool2d((5, 5)),                              # [B, 128, 5, 5]
)
```

### ❌ 主要差异

| 层 | NCNN | PyTorch | 问题 |
|----|------|---------|------|
| 第1层 | Conv(1→16, s2, p0) | Conv(1→32, s2, p1) | ⚠️ **通道数、padding不同** |
| 第2层 | Conv(16→32, s2, p0) | — | ❌ **PyTorch缺少此层** |
| 第4层后 | — | Conv(64→64, residual) | ❌ **PyTorch多出此层** |
| 第6-7层 | Conv with **dilation=2** | Conv without dilation | ❌ **缺少空洞卷积** |
| 最后 | 不使用池化 | AdaptiveAvgPool2d((5,5)) | ⚠️ **处理方式不同** |

---

## 🖼️ 图像编码器对比

### NCNN 实际结构（MobileNetV2）

```
Input: face [W, H, 6]

1. Padding(1,1,1,1, type=2)          pad_185
   → [W+2, H+2, 6]

2. Conv(6→16, k3, s1, p0, groups=1)  convrelu_6: 0=16 1=3 7=1
   → ReLU
   → [W, H, 16]

3. Conv(16→32, k3, s2, p1)           convrelu_7: 0=32 1=3 3=2 4=1
   → ReLU
   → [W/2, H/2, 32]

4. 第一个 Inverted Residual Block:
   DepthWise(32, k3, s1, p1) + Conv(32→16, k1)
   → GroupNorm → ReLU
   
5. 后续 MobileNetV2 标准结构
   - InvertedResidual(16→24, expand_ratio=6, stride=2)
   - InvertedResidual(24→24, expand_ratio=6, stride=1) ×2
   - InvertedResidual(24→32, expand_ratio=6, stride=2)
   - InvertedResidual(32→32, expand_ratio=6, stride=1) ×3
   - InvertedResidual(32→64, expand_ratio=6, stride=2)
   - InvertedResidual(64→64, expand_ratio=6, stride=1) ×4
   - InvertedResidual(64→96, expand_ratio=6, stride=1) ×3
   - InvertedResidual(96→160, expand_ratio=6, stride=2)
   - InvertedResidual(160→320, expand_ratio=6, stride=1)
```

### PyTorch 复现结构

```python
# backbone 第一层
self.backbone.features[0] = conv_bn(6, input_channel, 2, norm_type)
# input_channel = 32 (默认)

# 实际第一层：
Conv2d(6, 32, 3, 2, 1)  # stride=2
```

### ❌ 主要差异

| 项目 | NCNN | PyTorch | 问题 |
|------|------|---------|------|
| 预处理 | Padding(1,1,1,1) 再 Conv(s1) | 无padding，直接 Conv(s2) | ⚠️ **预处理方式不同** |
| 第1层 | Conv(6→16, k3, s1, p0) | Conv(6→32, k3, s2, p1) | ❌ **通道数、stride、padding都不同** |
| 第2层 | Conv(16→32, k3, s2, p1) | — | ❌ **PyTorch已在第1层完成** |

---

## 🔄 解码器对比

### NCNN 实际结构

```
解码器主要组成：
1. Deconvolution ×6 (上采样)
2. Concat (with skip connections)
3. Convolution + ConvolutionDepthWise blocks
4. GroupNorm + ReLU

输出层：
- Padding(1,1,1,1)
- Conv(8→3, k3, s1)
- TanH 激活
```

### PyTorch 复现结构

```python
# 解码器
self.dconv0 = nn.ConvTranspose2d(128, 128, kernel_size=1, stride=1, padding=0)
self.invres0 = InvertedResidual(448, 96, 1, 6, norm_type)

self.dconv1 = nn.ConvTranspose2d(96, 96, 3, padding=1, stride=2, output_padding=1)
self.invres1 = InvertedResidual(192, 96, 1, 6, norm_type)

self.dconv2 = nn.ConvTranspose2d(96, 32, 3, padding=1, stride=2, output_padding=1)
self.invres2 = InvertedResidual(64, 32, 1, 6, norm_type)

self.dconv3 = nn.ConvTranspose2d(32, 24, 3, padding=1, stride=2, output_padding=1)
self.invres3 = InvertedResidual(48, 24, 1, 6, norm_type)

self.dconv4 = nn.ConvTranspose2d(24, 16, 3, padding=1, stride=2, output_padding=1)
self.invres4 = InvertedResidual(32, 16, 1, 6, norm_type)

self.dconv5 = nn.ConvTranspose2d(16, 8, 3, padding=1, stride=2, output_padding=1)

# 输出层
self.conv_last = nn.Conv2d(8, 3, 1)
self.conv_score = nn.Conv2d(3, 3, 1)
x = torch.sigmoid(x)  # ❌ 激活函数错误
```

### ❌ 主要差异

| 项目 | NCNN | PyTorch | 问题 |
|------|------|---------|------|
| 输出激活 | **TanH** (范围 [-1, 1]) | **Sigmoid** (范围 [0, 1]) | ❌ **激活函数不同，影响训练和推理** |
| 最后一层 | Conv(3→3, k1) | Conv(3→3, k1) | ✅ 匹配 |
| Padding | 有 Padding 层 | 无 | ⚠️ 可能影响边缘效果 |

---

## 📐 归一化层对比

### NCNN 使用 GroupNorm

```
GroupNorm gn_59  1 1 27 28 0=1 1=24 2=1.000000e-05 3=1
参数说明:
- 0=1: num_groups = 1 (相当于 LayerNorm)
- 1=24: channels = 24
- 2=1e-05: epsilon
- 3=1: affine = True
```

### PyTorch 使用 InstanceNorm2d/BatchNorm2d

```python
# MobileNet.py 中
norm_type = nn.InstanceNorm2d  # 默认
# 或 nn.BatchNorm2d

# InvertedResidual 中
norm_type(hidden_dim)
```

### ❌ 归一化差异

| 特性 | GroupNorm (NCNN) | InstanceNorm2d (PyTorch) | 影响 |
|------|------------------|--------------------------|------|
| 作用范围 | 每个 group | 每个 instance | ⚠️ 统计量不同 |
| Batch依赖 | ❌ 否 | ❌ 否 | ✅ 都不依赖batch |
| 推理模式 | 相同 | 相同 | ✅ 推理时行为一致 |
| 训练行为 | 不同 | 不同 | ❌ **训练时需要转换** |

**建议**: 改用 `nn.GroupNorm(num_groups=1, num_channels=C)`

---

## 🔧 需要修改的地方

### 1️⃣ **音频编码器** (Critical)

```python
# ❌ 当前实现
self.audio_encoder = nn.Sequential(
    Conv2d(1, 32, kernel_size=3, stride=2, padding=1),  # 错误
    # ...
)

# ✅ 修改为
self.audio_encoder = nn.Sequential(
    # 第1层：1→16
    Conv2d(1, 16, kernel_size=3, stride=2, padding=0),  # 注意 padding=0
    
    # 第2层：16→32
    Conv2d(16, 32, kernel_size=3, stride=2, padding=0),  # 注意 padding=0
    
    # 第3层：32→32 + Residual
    Conv2d(32, 32, kernel_size=3, stride=1, padding=1, residual=True),
    
    # 第4层：32→64
    Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
    
    # 删除这一层 ❌
    # Conv2d(64, 64, kernel_size=3, stride=1, padding=1, residual=True),
    
    # 第5层：64→128
    Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
    
    # 第6层：128→128 (dilation=2)
    nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=1, dilation=2),  # ⚠️ 添加 dilation
    nn.BatchNorm2d(128),
    nn.ReLU(),
    
    # 第7层：128→128 (dilation=2, padding=2)
    nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=2, dilation=2),  # ⚠️ 添加 dilation
    nn.BatchNorm2d(128),
    nn.ReLU(),
    
    # 第8层：128→128 + Residual
    Conv2d(128, 128, kernel_size=3, stride=1, padding=1, residual=True),
)
# ❌ 删除 AdaptiveAvgPool2d - NCNN 不使用
```

### 2️⃣ **图像编码器第一层** (Critical)

```python
# ❌ 当前实现
self.features = [conv_bn(6, input_channel, 2, norm_type)]  # stride=2, 32通道

# ✅ 修改为
self.features = [
    nn.ZeroPad2d(1),  # 添加 padding
    nn.Conv2d(6, 16, 3, stride=1, padding=0, bias=False),  # 6→16, stride=1
    norm_type(16),
    nn.ReLU(inplace=True),
    
    nn.Conv2d(16, 32, 3, stride=2, padding=1, bias=False),  # 16→32, stride=2
    norm_type(32),
    nn.ReLU(inplace=True)
]
```

### 3️⃣ **归一化层** (Important)

```python
# ❌ 当前实现
norm_type = nn.InstanceNorm2d

# ✅ 修改为
norm_type = lambda channels: nn.GroupNorm(num_groups=1, num_channels=channels)
```

### 4️⃣ **输出激活函数** (Critical)

```python
# ❌ 当前实现
x = torch.sigmoid(x)

# ✅ 修改为
x = torch.tanh(x)
```

### 5️⃣ **输出层前的 Padding**

```python
# ✅ 在最后的卷积前添加
x = self.dconv5(x)
x = nn.functional.pad(x, (1, 1, 1, 1), mode='constant', value=0)  # 添加 padding
x = self.conv_last(x)
x = self.conv_score(x)
x = torch.tanh(x)
```

---

## 📋 修改后的完整音频编码器

```python
class AudioEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 16, 3, stride=2, padding=0),  # [B, 16, 127, 9]
            nn.BatchNorm2d(16),
            nn.ReLU()
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 3, stride=2, padding=0),  # [B, 32, 63, 4]
            nn.BatchNorm2d(32),
            nn.ReLU()
        )
        
        # Residual block
        self.conv3 = nn.Conv2d(32, 32, 3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(32)
        
        self.conv4 = nn.Sequential(
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        
        self.conv5 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        # Dilated convolutions
        self.conv6 = nn.Sequential(
            nn.Conv2d(128, 128, 3, stride=2, padding=1, dilation=2),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        self.conv7 = nn.Sequential(
            nn.Conv2d(128, 128, 3, stride=2, padding=2, dilation=2),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        # Final residual block
        self.conv8 = nn.Conv2d(128, 128, 3, stride=1, padding=1)
        self.bn8 = nn.BatchNorm2d(128)
        
    def forward(self, x):
        # x: [B, 1, 256, 20]
        x = self.conv1(x)
        x = self.conv2(x)
        
        # Residual
        identity = x
        x = self.conv3(x)
        x = self.bn3(x)
        x = x + identity
        x = F.relu(x)
        
        x = self.conv4(x)
        x = self.conv5(x)
        x = self.conv6(x)
        x = self.conv7(x)
        
        # Final residual
        identity = x
        x = self.conv8(x)
        x = self.bn8(x)
        x = x + identity
        x = F.relu(x)
        
        return x
```

---

## 📊 修改优先级

| 优先级 | 修改项 | 影响程度 | 必要性 |
|--------|--------|----------|--------|
| 🔴 P0 | 输出激活函数 (TanH vs Sigmoid) | 极高 | **必须** |
| 🔴 P0 | 音频编码器第1-2层通道数和padding | 极高 | **必须** |
| 🟠 P1 | 音频编码器 dilation 卷积 | 高 | **强烈建议** |
| 🟠 P1 | 图像编码器第一层结构 | 高 | **强烈建议** |
| 🟡 P2 | 归一化层类型 (GroupNorm) | 中 | 建议 |
| 🟡 P2 | 输出层前的 Padding | 中 | 建议 |
| 🟢 P3 | 删除 AdaptiveAvgPool2d | 低 | 可选 |

---

## 🧪 验证方法

### 1. 层数对比

```python
# 统计 PyTorch 模型层数
def count_layers(model):
    count = 0
    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d, 
                               nn.BatchNorm2d, nn.GroupNorm)):
            count += 1
    return count

# NCNN 模型: 165 层
# PyTorch 模型: 应该接近 165 层
```

### 2. 输出形状验证

```python
model = MobileNetV2Unet()
audio = torch.randn(1, 256, 20)
face = torch.randn(1, 6, 160, 160)

output = model(face, audio)
print(f"Output shape: {output.shape}")  # 应该是 [1, 3, 160, 160]
print(f"Output range: [{output.min():.3f}, {output.max():.3f}]")  # 应该是 [-1, 1]
```

### 3. 参数量对比

```python
# NCNN 模型参数量: ~3.77M
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params / 1e6:.2f}M")
# 应该接近 3.77M
```

---

## 📝 总结

### 主要问题

1. ❌ **音频编码器结构错误**：缺少 1→16 层，缺少 dilation 卷积
2. ❌ **图像编码器第一层错误**：通道数、stride 不匹配
3. ❌ **输出激活函数错误**：使用了 Sigmoid 而非 TanH
4. ⚠️ **归一化层类型不同**：InstanceNorm vs GroupNorm

### 修改建议

按照上述 **修改优先级** 逐步调整：
1. 先修改 **P0** 级别的问题（激活函数、音频编码器基础结构）
2. 再修改 **P1** 级别的问题（dilation、图像编码器）
3. 最后调整 **P2-P3** 级别的细节

### 预期效果

完成所有修改后：
- ✅ 网络结构与 NCNN 模型完全一致
- ✅ 可以正确加载 NCNN 的权重
- ✅ 推理结果与 NCNN 保持一致

