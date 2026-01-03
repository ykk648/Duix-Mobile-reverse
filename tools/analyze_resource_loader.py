#!/usr/bin/env python3
"""
resource_loader.jar 分析工具

分析混淆的 JAR 文件，提取关键信息（文件路径、字符串等）
"""

import zipfile
import re
import sys
import os

def analyze_jar(jar_path):
    """分析 JAR 文件"""
    print("=" * 60)
    print("🔍 resource_loader.jar 分析工具")
    print("=" * 60)
    print(f"📥 JAR 文件: {jar_path}")
    print()
    
    with zipfile.ZipFile(jar_path, 'r') as jar:
        # 列出所有文件
        print("📋 JAR 内容:")
        for name in sorted(jar.namelist()):
            info = jar.getinfo(name)
            print(f"   {name} ({info.file_size} bytes)")
        print()
        
        # 分析每个 class 文件
        for name in jar.namelist():
            if name.endswith('.class'):
                print(f"\n{'='*60}")
                print(f"📦 分析: {name}")
                print('='*60)
                
                data = jar.read(name)
                
                # 提取字符串
                try:
                    # 尝试解码为 UTF-8
                    text = data.decode('utf-8', errors='ignore')
                    
                    # 查找关键字符串
                    keywords = [
                        'wenet', 'onnx', 'model', 'file', 'path',
                        'decrypt', 'aes', 'gjdigits', '.p', '.b', '.j',
                        'setWenetfn', 'getWenetfn', 'wenetfn'
                    ]
                    
                    found_keywords = []
                    for keyword in keywords:
                        if keyword.lower() in text.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"✅ 找到关键字: {', '.join(found_keywords)}")
                    
                    # 查找文件路径模式
                    patterns = [
                        r'[a-zA-Z0-9_/\.-]*wenet[a-zA-Z0-9_/\.-]*\.(onnx|p|b|j)',
                        r'[a-zA-Z0-9_/\.-]*\.(onnx|p|b|j|bin)',
                        r'[a-zA-Z0-9_/\.-]{5,50}\.(onnx|p|b|j|bin)',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            print(f"\n📁 找到文件路径模式 ({pattern}):")
                            for m in set(matches)[:10]:
                                if isinstance(m, tuple):
                                    print(f"   {m[0] if m[0] else m}")
                                else:
                                    print(f"   {m}")
                    
                    # 查找方法名
                    method_patterns = [
                        r'setWenetfn',
                        r'getWenetfn',
                        r'wenetfn',
                    ]
                    
                    for pattern in method_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            print(f"\n🔧 找到方法: {pattern}")
                    
                    # 如果是混淆的类，显示更多信息
                    if '/a/' in name or '/b/' in name:
                        print(f"\n⚠️  这是混淆的类")
                        # 尝试提取更多字符串
                        strings = re.findall(r'[a-zA-Z0-9_/\.-]{3,30}', text)
                        unique_strings = sorted(set(strings))
                        print(f"\n📝 提取的字符串 (前20个):")
                        for s in unique_strings[:20]:
                            if len(s) > 3:
                                print(f"   {s}")
                
                except Exception as e:
                    print(f"❌ 分析失败: {e}")
                
                # 使用 strings 命令提取可打印字符串
                print(f"\n🔤 可打印字符串:")
                import subprocess
                try:
                    # 写入临时文件
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.class') as tmp:
                        tmp.write(data)
                        tmp_path = tmp.name
                    
                    # 使用 strings 命令
                    result = subprocess.run(['strings', tmp_path], 
                                           capture_output=True, text=True)
                    if result.returncode == 0:
                        strings = result.stdout.strip().split('\n')
                        # 过滤和显示相关字符串
                        relevant = [s for s in strings if any(kw in s.lower() 
                            for kw in ['wenet', 'onnx', 'model', 'file', 'path', 
                                      'decrypt', 'aes', '.p', '.b', '.j', '.onnx'])]
                        if relevant:
                            for s in relevant[:30]:
                                print(f"   {s}")
                        else:
                            print("   (未找到相关字符串)")
                    
                    os.unlink(tmp_path)
                except Exception as e:
                    print(f"   (无法提取字符串: {e})")

def main():
    jar_path = "Duix-Mobile/duix-android/dh_aigc_android/duix-sdk/libs/resource_loader.jar"
    
    if len(sys.argv) > 1:
        jar_path = sys.argv[1]
    
    if not os.path.exists(jar_path):
        print(f"❌ JAR 文件不存在: {jar_path}")
        sys.exit(1)
    
    analyze_jar(jar_path)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

