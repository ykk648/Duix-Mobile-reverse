#!/usr/bin/env python3
"""
NCNN 模型加密脚本

将 NCNN 模型文件加密成 Duix 可以直接加载的格式

用法:
    python encrypt_ncnn_model.py <input_file> <output_file>
    
示例:
    python encrypt_ncnn_model.py model.ncnn.bin model.ncnn.bin.encrypted
    python encrypt_ncnn_model.py model.ncnn.param dh_model.p
"""

import sys
import struct
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# AES 加密密钥和 IV（与 Duix 保持一致）
KEY = b"yymrjzbwyrbjszrk"
IV = b"yymrjzbwyrbjszrk"

# 文件头魔数
MAGIC = b'gjdigits'

def encrypt_file(input_file, output_file):
    """加密文件为 Duix 格式"""
    print(f"🔐 正在加密: {input_file} -> {output_file}")
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 错误：输入文件不存在: {input_file}")
        return False
    
    # 读取原始文件
    with open(input_path, 'rb') as f:
        plain_data = f.read()
    
    real_size = len(plain_data)
    print(f"   📏 原始文件大小: {real_size:,} bytes ({real_size / 1024 / 1024:.2f} MB)")
    
    # AES-128-CBC 加密（需要16字节对齐）
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    
    # 填充数据到16字节对齐
    padded_data = pad(plain_data, AES.block_size)
    
    # 加密
    encrypted_data = cipher.encrypt(padded_data)
    
    print(f"   📦 加密后大小: {len(encrypted_data):,} bytes ({len(encrypted_data) / 1024 / 1024:.2f} MB)")
    
    # 写入加密文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as out:
        # 写入魔数
        out.write(MAGIC)
        
        # 写入原始文件大小（uint64_t, little-endian）
        out.write(struct.pack('<Q', real_size))
        
        # 写入16字节保留字段（全0）
        out.write(b'\x00' * 16)
        
        # 写入加密数据
        out.write(encrypted_data)
    
    print(f"   ✅ 加密成功！输出: {output_file}")
    print(f"   📁 输出文件大小: {output_path.stat().st_size:,} bytes")
    return True

def main():
    if len(sys.argv) != 3:
        print("用法: python encrypt_ncnn_model.py <input_file> <output_file>")
        print("\n示例:")
        print("  # 加密 bin 文件")
        print("  python encrypt_ncnn_model.py model.ncnn.bin dh_model.b")
        print("\n  # 加密 param 文件")
        print("  python encrypt_ncnn_model.py model.ncnn.param dh_model.p")
        print("\n  # 加密配置文件")
        print("  python encrypt_ncnn_model.py config.json config.j")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("=" * 60)
    print("🔐 NCNN 模型加密工具")
    print("=" * 60)
    
    success = encrypt_file(input_file, output_file)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 加密完成！")
        print("=" * 60)
        print("\n📝 提示:")
        print("   - 加密后的文件可以直接被 Duix SDK 加载")
        print("   - 文件格式: gjdigits 魔数 + 原始大小 + 保留字段 + AES加密数据")
        print("   - 加密算法: AES-128-CBC")
        print("   - 密钥/IV: yymrjzbwyrbjszrk")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()


