#!/usr/bin/env python3
"""
WeNet ONNX 模型解密工具

从加密的 wenet.onnx 文件中解密出标准的 ONNX 模型文件。
加密方式与 dh_model.p/b 相同：AES-128-CBC
"""

import struct
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# AES 密钥和 IV（与 dh_model 相同）
KEY = b"yymrjzbwyrbjszrk"
IV = b"yymrjzbwyrbjszrk"

def decrypt_wenet(input_file, output_file):
    """
    解密 WeNet ONNX 模型文件
    
    Args:
        input_file: 加密的 wenet.onnx 文件路径
        output_file: 解密后的输出文件路径
    """
    with open(input_file, 'rb') as f:
        # 读取文件头
        magic = f.read(8)
        if magic != b'gjdigits':
            print(f"❌ 错误：不是有效的加密文件，魔数: {magic}")
            return False
        
        # 读取原始文件大小
        real_size = struct.unpack('<Q', f.read(8))[0]
        f.read(16)  # 跳过保留字段
        
        print(f"✅ 魔数: {magic.decode('ascii', errors='ignore')}")
        print(f"📏 原始文件大小: {real_size:,} bytes ({real_size / 1024 / 1024:.2f} MB)")
        
        # 读取加密数据
        encrypted_data = f.read()
        print(f"📦 加密数据大小: {len(encrypted_data):,} bytes")
        
        # AES-128-CBC 解密
        print("🔓 正在解密...")
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 截取实际大小
        decrypted_data = decrypted_data[:real_size]
        
        # 验证 ONNX 文件格式
        if decrypted_data[:4] != b'\x08\x03\x12':
            # ONNX 文件通常以 protobuf 格式开始
            # 检查是否是有效的 ONNX 文件
            if b'onnx' not in decrypted_data[:100].lower():
                print("⚠️  警告：解密后的文件可能不是有效的 ONNX 格式")
        
        # 写入解密后的文件
        with open(output_file, 'wb') as out:
            out.write(decrypted_data)
        
        print(f"✅ 解密成功！")
        print(f"📁 输出文件: {output_file}")
        print(f"📏 解密后大小: {len(decrypted_data):,} bytes ({len(decrypted_data) / 1024 / 1024:.2f} MB)")
        
        # 显示文件头部（前32字节）
        print("\n📋 文件头部（前32字节，十六进制）:")
        print(' '.join(f'{b:02x}' for b in decrypted_data[:32]))
        
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python decrypt_wenet.py <加密的wenet文件> <输出onnx文件>")
        print("\n示例:")
        print("  python decrypt_wenet.py encrypted_wenet.onnx wenet.onnx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("=" * 60)
    print("🔐 WeNet ONNX 模型解密工具")
    print("=" * 60)
    print(f"📥 输入文件: {input_file}")
    print(f"📤 输出文件: {output_file}")
    print()
    
    success = decrypt_wenet(input_file, output_file)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 解密完成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 解密失败！")
        print("=" * 60)
        sys.exit(1)

