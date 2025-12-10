#!/usr/bin/env python3
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

key = b"yymrjzbwyrbjszrk"
iv = b"yymrjzbwyrbjszrk"

def decrypt_file(input_file, output_file):
    with open(input_file, 'rb') as f:
        # 读取头部
        magic = f.read(8)
        if magic != b'gjdigits':
            print(f"错误：不是有效的加密文件，魔数: {magic}")
            return False
        
        # 读取文件大小信息
        real_size = struct.unpack('<Q', f.read(8))[0]
        f.read(16)  # 跳过其他头部信息
        
        print(f"魔数: {magic}")
        print(f"原始文件大小: {real_size} bytes")
        
        # 读取加密数据
        encrypted_data = f.read()
        
        # AES-128-CBC 解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 截取实际大小
        decrypted_data = decrypted_data[:real_size]
        
        # 写入解密后的文件
        with open(output_file, 'wb') as out:
            out.write(decrypted_data)
        
        print(f"解密成功！输出文件: {output_file}")
        print(f"解密后大小: {len(decrypted_data)} bytes")
        
        # 显示文件头部（前100字节）
        print("\n文件头部（前100字节）:")
        print(decrypted_data[:100].hex())
        
        # 尝试判断文件类型
        if decrypted_data[:4] == b'\x7fELF':
            print("文件类型: ELF 二进制")
        elif decrypted_data[:2] == b'PK':
            print("文件类型: ZIP/JAR")
        elif decrypted_data[:8] == b'\x89PNG\r\n\x1a\n':
            print("文件类型: PNG图片")
        elif decrypted_data[:2] == b'\xff\xd8':
            print("文件类型: JPEG图片")
        elif b'ncnn' in decrypted_data[:100] or b'7767517' in decrypted_data[:100]:
            print("文件类型: 可能是 NCNN 模型文件")
            # 尝试解析 ncnn param 文件
            try:
                text = decrypted_data[:500].decode('utf-8', errors='ignore')
                print("\n文件内容预览:")
                print(text)
            except:
                pass
        
        return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("用法: python decrypt_model.py <输入文件> <输出文件>")
        sys.exit(1)
    
    decrypt_file(sys.argv[1], sys.argv[2])
