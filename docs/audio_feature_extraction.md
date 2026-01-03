# 音频特征提取（WeNet）文档

## 📋 概述

Duix Mobile SDK 使用 **WeNet ONNX 模型**进行音频特征提取，将音频 PCM 数据转换为 BNF（Bottleneck Features）特征向量，供后续的人脸生成模型使用。

---

## 🔍 模型信息

### 模型规格

| 项目 | 值 |
|------|-----|
| **格式** | ONNX (.onnx) |
| **推理引擎** | ONNX Runtime |
| **模型名称** | `wenet.onnx` |
| **加密方式** | AES-128-CBC（与 dh_model 相同） |

### 输入/输出

#### 输入
| 名称 | 类型 | 维度 | 说明 |
|------|------|------|------|
| `speech` | float32 | `[1, melcnt, 80]` | Mel 频谱特征 |
| `speech_lengths` | int32 | `[1]` | Mel 特征的长度 |

**默认参数**：
- `melcnt = 321` (Mel 特征帧数)
- Mel 维度：80

#### 输出
| 名称 | 类型 | 维度 | 说明 |
|------|------|------|------|
| `encoder_out` | float32 | `[1, bnfcnt, 256]` | 音频特征向量（BNF） |

**默认参数**：
- `bnfcnt = 79` (BNF 特征帧数)
- BNF 维度：256

---

## 🔐 模型解密

### 解密工具

使用 `tools/decrypt_wenet.py` 解密加密的 WeNet ONNX 模型：

```bash
python tools/decrypt_wenet.py encrypted_wenet.onnx wenet.onnx
```

### 加密方式

与 NCNN 模型文件相同：
- **算法**: AES-128-CBC
- **密钥**: `yymrjzbwyrbjszrk` (16字节)
- **IV**: `yymrjzbwyrbjszrk` (16字节)
- **文件头**: `gjdigits` (8字节魔数)

### 文件格式

```
+-------------------+
| "gjdigits" (8字节) | <- 文件头魔数
+-------------------+
| 原始大小 (8字节)   | <- uint64_t, 小端序
+-------------------+
| 加密数据           | <- AES-CBC 加密
+-------------------+
```

---

## 🎤 音频处理流程

### 完整流程

```
PCM 音频数据 (16kHz, mono)
    ↓
MFCC 特征提取
    ↓
Mel 频谱特征 [melcnt, 80]
    ↓
WeNet ONNX 推理
    ↓
BNF 特征向量 [bnfcnt, 256]
    ↓
供人脸生成模型使用
```

### 详细步骤

#### 1. 音频加载

```python
import librosa

# 加载音频文件（自动重采样到 16kHz）
audio_data, sample_rate = librosa.load("audio.wav", sr=16000, mono=True)
```

**要求**：
- 采样率：16000 Hz
- 声道：单声道（mono）
- 格式：WAV/PCM

#### 2. MFCC 特征提取

```python
import librosa

# 提取 Mel 频谱特征
mel_spec = librosa.feature.melspectrogram(
    y=audio_data,
    sr=16000,
    n_mels=80,          # Mel 滤波器数量
    hop_length=160,     # 帧移（10ms）
    n_fft=512,
    fmin=0,
    fmax=8000
)

# 转换为对数尺度
mel_log = librosa.power_to_db(mel_spec, ref=np.max)

# 归一化
mel_log = (mel_log - mel_log.min()) / (mel_log.max() - mel_log.min() + 1e-8)

# 转置：[n_mels, time] -> [time, n_mels]
mel_features = mel_log.T  # [time, 80]
```

**参数说明**：
- `n_mels=80`: Mel 滤波器数量（对应模型输入维度）
- `hop_length=160`: 帧移，对应 10ms（16000 Hz * 0.01s = 160）
- `n_fft=512`: FFT 窗口大小

#### 3. 特征填充/截断

```python
import numpy as np

def pad_or_truncate_mel(mel_features, target_length=321):
    """填充或截断到目标长度"""
    current_length = mel_features.shape[0]
    
    if current_length < target_length:
        # 填充零
        pad_length = target_length - current_length
        pad = np.zeros((pad_length, 80), dtype=np.float32)
        padded_mel = np.concatenate([mel_features, pad], axis=0)
    elif current_length > target_length:
        # 截断
        padded_mel = mel_features[:target_length]
    else:
        padded_mel = mel_features
    
    return padded_mel

mel_features = pad_or_truncate_mel(mel_features, target_length=321)
```

#### 4. WeNet ONNX 推理

```python
import onnxruntime as ort
import numpy as np

# 初始化 ONNX Runtime
sess_options = ort.SessionOptions()
sess_options.intra_op_num_threads = 2
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

session = ort.InferenceSession("wenet.onnx", sess_options=sess_options)

# 准备输入
speech_input = mel_features.reshape(1, 321, 80).astype(np.float32)  # [1, 321, 80]
speech_lengths = np.array([321], dtype=np.int32)  # [1]

# 执行推理
inputs = {
    "speech": speech_input,
    "speech_lengths": speech_lengths
}
outputs = session.run(["encoder_out"], inputs)

# 获取输出
bnf_features = outputs[0][0]  # [79, 256]
```

---

## 💻 使用示例

### 完整示例代码

参见 `examples/audio_inference.py`：

```bash
# 解密 WeNet 模型
python tools/decrypt_wenet.py encrypted_wenet.onnx wenet.onnx

# 提取音频特征
python examples/audio_inference.py wenet.onnx audio.wav output_bnf.npy
```

### Python API 使用

```python
from examples.audio_inference import WeNetInference

# 初始化推理引擎
wenet = WeNetInference("wenet.onnx", melcnt=321, bnfcnt=79)

# 处理音频文件
bnf_features = wenet.process_audio_file("audio.wav")

# 或手动处理
import librosa
audio_data, sr = librosa.load("audio.wav", sr=16000, mono=True)
mel_features = wenet.extract_mfcc(audio_data, sr)
bnf_features = wenet.infer(mel_features)

print(f"BNF 特征形状: {bnf_features.shape}")  # (79, 256)
```

---

## 📊 特征维度计算

### Mel 帧数计算

```python
def calculate_mel_frames(pcm_samples, hop_length=160):
    """计算 Mel 特征帧数"""
    mel_frames = pcm_samples // hop_length + 1
    return mel_frames

# 示例：1秒音频（16000 样本）
mel_frames = calculate_mel_frames(16000)  # 101 帧
```

### BNF 帧数计算

```python
def calculate_bnf_frames(mel_frames):
    """计算 BNF 特征帧数"""
    # 根据 Duix SDK 的实现
    bnf_frames = int(mel_frames * 0.25 - 0.75)
    return max(1, bnf_frames)  # 至少 1 帧

# 示例：321 帧 Mel -> 79 帧 BNF
bnf_frames = calculate_bnf_frames(321)  # 79 帧
```

---

## 🔧 参数配置

### 默认配置

| 参数 | 值 | 说明 |
|------|-----|------|
| `melcnt` | 321 | Mel 特征帧数 |
| `bnfcnt` | 79 | BNF 特征帧数 |
| `n_mels` | 80 | Mel 滤波器数量 |
| `hop_length` | 160 | 帧移（10ms） |
| `sample_rate` | 16000 | 音频采样率 |
| `n_fft` | 512 | FFT 窗口大小 |

### 动态配置

根据实际音频长度动态计算：

```python
# 计算实际需要的 Mel 帧数
pcm_samples = len(audio_data)
mel_frames = pcm_samples // 160 + 1

# 计算对应的 BNF 帧数
bnf_frames = int(mel_frames * 0.25 - 0.75)

# 创建推理引擎（使用动态维度）
wenet = WeNetInference("wenet.onnx", melcnt=mel_frames, bnfcnt=bnf_frames)
```

---

## 📝 注意事项

1. **音频格式要求**：
   - 采样率：16000 Hz
   - 声道：单声道
   - 格式：WAV/PCM

2. **特征对齐**：
   - Mel 特征需要填充或截断到 `melcnt` 长度
   - 默认使用 `melcnt=321`

3. **性能优化**：
   - ONNX Runtime 使用 2 个线程
   - 启用图优化
   - 禁用预打包（`disable_prepacking`）

4. **内存管理**：
   - Mel 特征：`[melcnt, 80]` float32 ≈ `melcnt * 80 * 4` bytes
   - BNF 特征：`[bnfcnt, 256]` float32 ≈ `bnfcnt * 256 * 4` bytes

---

## 🔗 相关文档

- [模型文件加密分析](encryption_analysis.md) - 加密机制详解
- [NCNN 推理流程分析](ncnn_inference_analysis.md) - 人脸生成模型推理
- [音频特征推理模型说明](../../duix-android/音频特征推理模型说明.md) - Android SDK 实现细节

---

## 📌 参考实现

### C++ 实现（Android SDK）

- `dhmfcc/wenetai.cpp` - ONNX Runtime 推理实现
- `dhmfcc/dhwenet.cpp` - MFCC 特征提取
- `dhmfcc/dhpcm.cpp` - PCM 数据处理

### Python 实现（本项目）

- `examples/audio_inference.py` - 完整的音频推理示例
- `tools/decrypt_wenet.py` - 模型解密工具

