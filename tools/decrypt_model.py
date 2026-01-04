#!/usr/bin/env python3
"""
NCNN 模型解密脚本

解密 Duix 使用的 AES-128-CBC 加密模型文件

用法:
    python decrypt_model.py <input_file> <output_file>
    
示例:
    python decrypt_model.py dh_model.p output/dh_model.param
    python decrypt_model.py dh_model.b output/dh_model.bin
    python decrypt_model.py config.j output/config.json
"""

import sys
import struct
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# AES 解密密钥和 IV（与 Duix 保持一致）
KEY = b"yymrjzbwyrbjszrk"
IV = b"yymrjzbwyrbjszrk"

# 文件头魔数
MAGIC = b'gjdigits'

def decrypt_file(input_file, output_file):
    """解密 Duix 格式的加密文件"""
    print(f"🔓 正在解密: {input_file} -> {output_file}")
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 错误：输入文件不存在: {input_file}")
        return False
    
    with open(input_path, 'rb') as f:
        # 读取文件头
        magic = f.read(8)
        if magic != MAGIC:
            print(f"❌ 错误：不是有效的加密文件，魔数: {magic}")
            return False
        
        # 读取原始文件大小
        real_size = struct.unpack('<Q', f.read(8))[0]
        f.read(16)  # 跳过保留字段
        
        print(f"   📏 原始文件大小: {real_size:,} bytes ({real_size / 1024 / 1024:.2f} MB)")
        
        # 读取加密数据
        encrypted_data = f.read()
        
        # AES-128-CBC 解密
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 截取实际大小
        decrypted_data = decrypted_data[:real_size]
        
        # 写入解密后的文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as out:
            out.write(decrypted_data)
        
        print(f"   ✅ 解密成功！输出: {output_file}")
        print(f"   📁 解密后大小: {len(decrypted_data):,} bytes")
        
        # 尝试判断文件类型
        file_type = "未知"
        if decrypted_data[:4] == b'\x7fELF':
            file_type = "ELF 二进制"
        elif decrypted_data[:2] == b'PK':
            file_type = "ZIP/JAR"
        elif decrypted_data[:8] == b'\x89PNG\r\n\x1a\n':
            file_type = "PNG 图片"
        elif decrypted_data[:2] == b'\xff\xd8':
            file_type = "JPEG 图片"
        elif b'7767517' in decrypted_data[:100]:
            file_type = "NCNN Param 文件"
            # 尝试解析 ncnn param 文件
            try:
                text = decrypted_data[:500].decode('utf-8', errors='ignore')
                print(f"\n   📋 文件内容预览:")
                print("   " + "\n   ".join(text.split('\n')[:5]))
            except:
                pass
        elif decrypted_data[:4] == b'{' or decrypted_data[:4] == b'[':
            file_type = "JSON 文件"
            try:
                import json
                json_data = json.loads(decrypted_data.decode('utf-8'))
                print(f"\n   📋 JSON 内容:")
                import json as json_module
                print("   " + "\n   ".join(json_module.dumps(json_data, indent=2, ensure_ascii=False).split('\n')[:10]))
            except:
                pass
        
        print(f"   📄 文件类型: {file_type}")
        
        return True

def main():
    if len(sys.argv) != 3:
        print("用法: python decrypt_model.py <input_file> <output_file>")
        print("\n示例:")
        print("  # 解密 param 文件")
        print("  python decrypt_model.py dh_model.p output/dh_model.param")
        print("\n  # 解密 bin 文件")
        print("  python decrypt_model.py dh_model.b output/dh_model.bin")
        print("\n  # 解密配置文件")
        print("  python decrypt_model.py config.j output/config.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("=" * 60)
    print("🔓 NCNN 模型解密工具")
    print("=" * 60)
    
    success = decrypt_file(input_file, output_file)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 解密完成！")
        print("=" * 60)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
