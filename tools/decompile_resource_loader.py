#!/usr/bin/env python3
"""
resource_loader.jar 反编译工具

使用 javap 反编译混淆的 Java 类文件
"""

import subprocess
import os
import sys
import zipfile
import tempfile
import shutil

def extract_jar(jar_path, extract_dir):
    """解压 JAR 文件"""
    with zipfile.ZipFile(jar_path, 'r') as jar:
        jar.extractall(extract_dir)
    print(f"✅ 已解压 JAR 到: {extract_dir}")

def decompile_class(class_file, output_file=None):
    """使用 javap 反编译 class 文件"""
    try:
        # 使用 javap 反编译
        cmd = ['javap', '-c', '-p', '-l', class_file]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(class_file))
        
        if result.returncode == 0:
            decompiled = result.stdout
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(decompiled)
            return decompiled
        else:
            print(f"❌ 反编译失败: {result.stderr}")
            return None
    except FileNotFoundError:
        print("❌ 未找到 javap 命令，请安装 JDK")
        return None

def find_class_files(extract_dir):
    """查找所有 class 文件"""
    class_files = []
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.class'):
                class_files.append(os.path.join(root, file))
    return sorted(class_files)

def main():
    jar_path = "Duix-Mobile/duix-android/dh_aigc_android/duix-sdk/libs/resource_loader.jar"
    output_dir = "/tmp/resource_loader_decompiled"
    
    if len(sys.argv) > 1:
        jar_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    if not os.path.exists(jar_path):
        print(f"❌ JAR 文件不存在: {jar_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🔍 resource_loader.jar 反编译工具")
    print("=" * 60)
    print(f"📥 JAR 文件: {jar_path}")
    print(f"📤 输出目录: {output_dir}")
    print()
    
    # 创建临时解压目录
    temp_extract = tempfile.mkdtemp(prefix="resource_loader_")
    
    try:
        # 解压 JAR
        extract_jar(jar_path, temp_extract)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 查找所有 class 文件
        class_files = find_class_files(temp_extract)
        print(f"\n📋 找到 {len(class_files)} 个 class 文件")
        
        # 反编译每个文件
        for class_file in class_files:
            # 计算相对路径
            rel_path = os.path.relpath(class_file, temp_extract)
            # 转换为输出路径（.class -> .java）
            output_path = os.path.join(output_dir, rel_path.replace('.class', '.java'))
            output_dir_path = os.path.dirname(output_path)
            os.makedirs(output_dir_path, exist_ok=True)
            
            print(f"🔨 反编译: {rel_path}")
            decompiled = decompile_class(class_file, output_path)
            
            if decompiled:
                print(f"   ✅ 已保存到: {output_path}")
            else:
                print(f"   ❌ 反编译失败")
        
        print("\n" + "=" * 60)
        print(f"✅ 反编译完成！输出目录: {output_dir}")
        print("=" * 60)
        
        # 显示关键文件
        print("\n📌 关键文件:")
        key_files = [
            "ai/guiji/duix/sdk/client/loader/ModelInfoLoader.java",
            "ai/guiji/duix/sdk/client/loader/ModelInfo.java",
            "a/a.java",  # 混淆的类
            "a/b.java",  # 混淆的类
        ]
        for key_file in key_files:
            full_path = os.path.join(output_dir, key_file)
            if os.path.exists(full_path):
                print(f"   ✅ {key_file}")
            else:
                print(f"   ❌ {key_file} (未找到)")
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_extract, ignore_errors=True)

if __name__ == "__main__":
    main()

