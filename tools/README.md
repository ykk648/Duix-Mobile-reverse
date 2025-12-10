# 🔧 工具脚本

本目录包含用于分析和处理 DUIX 模型的工具。

## 📁 文件说明

| 文件 | 描述 |
|------|------|
| `decrypt_model.py` | NCNN 模型文件解密工具 |

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

## 📚 更多信息

详细的加密分析请参考：[加密机制分析](../docs/encryption_analysis.md)

