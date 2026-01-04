# 🔧 工具脚本

本目录包含用于分析和处理 DUIX 模型的工具。

## 📁 文件说明

| 文件 | 描述 |
|------|------|
| `decrypt_model.py` | NCNN 模型文件解密工具（dh_model.p/b, config.j, bbox.j） |
| `encrypt_ncnn_model.py` | NCNN 模型文件加密工具（将模型加密为 Duix 格式） |
| `merge_video_frames.py` | 视频帧合成工具（将 .sij 帧文件合并成视频） |
| `decrypt_wenet.py` | WeNet ONNX 模型解密工具 |

---

## 🔐 decrypt_model.py

解密 DUIX 使用的 AES-128-CBC 加密模型文件。

### 依赖安装

```bash
pip install pycryptodome
```

### 使用方法

```bash
# 解密 .param 文件（网络结构）
python decrypt_model.py path/to/dh_model.p output/decrypted.param

# 解密 .bin 文件（模型权重）
python decrypt_model.py path/to/dh_model.b output/decrypted.bin

# 解密配置文件
python decrypt_model.py path/to/config.j output/config.json
```

### 加密文件列表

DUIX 模型目录中的加密文件：

| 文件 | 内容 |
|------|------|
| `dh_model.p` | NCNN 网络结构 (.param) |
| `dh_model.b` | NCNN 模型权重 (.bin) |
| `config.j` | JSON 配置文件 |
| `bbox.j` | 边界框配置 |

### 加密参数

| 参数 | 值 |
|------|-----|
| **算法** | AES-128-CBC |
| **密钥** | `yymrjzbwyrbjszrk` |
| **IV** | `yymrjzbwyrbjszrk` |
| **文件头** | `gjdigits` (8字节) |

### 文件格式

加密文件结构：

```
+-------------------+
| "gjdigits" (8字节) | <- 文件头魔数
+-------------------+
| 原始大小 (8字节)   | <- uint64_t, 小端序
+-------------------+
| 加密数据           | <- AES-CBC 加密，16字节对齐
+-------------------+
```

### 解密后的文件

解密后得到标准的 NCNN 模型文件：

**decrypted.param** (文本格式)：
```
7767517
185 206
Input       audio    0 1 audio
Input       face     0 1 face
Padding     pad_0    1 1 face ...
Convolution conv_0   1 1 ...
...
```

**decrypted.bin** (二进制格式)：
- 包含所有层的权重数据
- 按层顺序存储
- float32 格式

### 代码示例

```python
from Crypto.Cipher import AES

def decrypt_file(input_path, output_path):
    key = b'yymrjzbwyrbjszrk'
    iv = b'yymrjzbwyrbjszrk'
    
    with open(input_path, 'rb') as f:
        # 读取头部
        header = f.read(8)
        if header != b'gjdigits':
            raise ValueError("Invalid file header")
        
        # 读取原始大小
        original_size = int.from_bytes(f.read(8), 'little')
        
        # 读取加密数据
        encrypted_data = f.read()
    
    # AES 解密
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_data)
    
    # 截取原始大小
    decrypted = decrypted[:original_size]
    
    with open(output_path, 'wb') as f:
        f.write(decrypted)

# 使用
decrypt_file('dh_model.p', 'model.param')
decrypt_file('dh_model.b', 'model.bin')
```

---

## 🔐 encrypt_ncnn_model.py

将 NCNN 模型文件加密成 Duix 可以直接加载的格式。

### 依赖安装

```bash
pip install pycryptodome
```

### 使用方法

```bash
# 加密 bin 文件（模型权重）
python encrypt_ncnn_model.py mobilenetv5_unet_wenet.ncnn.bin dh_model.b

# 加密 param 文件（网络结构）
python encrypt_ncnn_model.py mobilenetv5_unet_wenet.ncnn.param dh_model.p

# 加密配置文件
python encrypt_ncnn_model.py config.json config.j
```

### 加密参数

| 参数 | 值 |
|------|-----|
| **算法** | AES-128-CBC |
| **密钥** | `yymrjzbwyrbjszrk` |
| **IV** | `yymrjzbwyrbjszrk` |
| **文件头** | `gjdigits` (8字节) |

### 文件格式

加密后的文件格式与 `decrypt_model.py` 解密的格式相同：

```
+-------------------+
| "gjdigits" (8字节) | <- 文件头魔数
+-------------------+
| 原始大小 (8字节)   | <- uint64_t, 小端序
+-------------------+
| 保留字段 (16字节)  | <- 全0
+-------------------+
| 加密数据           | <- AES-CBC 加密，16字节对齐
+-------------------+
```

---

## 🎬 merge_video_frames.py

将 `.sij` 帧文件合并成视频文件。`.sij` 文件实际上是 JPEG 格式的图片，可以用于视频合成。

### 依赖安装

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载 https://ffmpeg.org/download.html
```

### 使用方法

```bash
# 基本用法（默认 25 fps）
python merge_video_frames.py raw_jpgs output.mp4

# 指定帧率
python merge_video_frames.py raw_jpgs output.mp4 --fps 30

# 使用相对路径
python merge_video_frames.py ./frames video.mp4 --fps 24
```

### 参数说明

- `frames_dir`: 包含 `.sij` 帧文件的目录
- `output_video`: 输出视频文件路径
- `--fps`: 视频帧率（默认: 25）

### 工作原理

1. 扫描指定目录中的所有 `.sij` 文件
2. 按文件名数字顺序排序
3. 使用 `ffmpeg` 的 `concat` demuxer 合并帧
4. 输出 H.264 编码的 MP4 视频文件

### 注意事项

- 确保目录中包含 `.sij` 文件
- 文件名应为数字（如 `0.sij`, `1.sij`, `2.sij`），否则可能无法正确排序
- 需要安装 `ffmpeg` 工具

---

## 📚 更多信息

详细的加密分析请参考：[加密机制分析](../docs/encryption_analysis.md)

