#!/usr/bin/env python3
"""
视频帧合成脚本

将 .sij 帧文件合并成视频文件

用法:
    python merge_video_frames.py <frames_dir> <output_video> [--fps FPS]
    
示例:
    python merge_video_frames.py raw_jpgs output.mp4
    python merge_video_frames.py raw_jpgs output.mp4 --fps 25
"""

import sys
import subprocess
import argparse
from pathlib import Path

def merge_frames_to_video(frames_dir, output_video, fps=25):
    """将 .sij 帧文件合并成视频"""
    print(f"\n🎬 正在合并帧为视频...")
    print(f"   输入目录: {frames_dir}")
    print(f"   输出视频: {output_video}")
    print(f"   帧率: {fps} fps")
    
    frames_dir = Path(frames_dir)
    
    if not frames_dir.exists():
        print(f"❌ 错误：目录不存在: {frames_dir}")
        return False
    
    # 获取所有 .sij 文件并按数字排序
    sij_files = sorted(
        frames_dir.glob("*.sij"),
        key=lambda x: int(x.stem) if x.stem.isdigit() else float('inf')
    )
    
    if not sij_files:
        print("❌ 错误：未找到 .sij 文件")
        return False
    
    print(f"   📸 找到 {len(sij_files)} 帧")
    
    # 使用 ffmpeg 合并视频
    # 由于 .sij 文件实际上是 JPEG 格式，可以直接使用
    try:
        # 使用 ffmpeg 的 concat demuxer
        concat_file = frames_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for sij_file in sij_files:
                f.write(f"file '{sij_file.absolute()}'\n")
                f.write(f"duration {1.0/fps}\n")
            # 最后一帧需要指定持续时间
            f.write(f"file '{sij_files[-1].absolute()}'\n")
        
        output_path = Path(output_video)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            str(output_path)
        ]
        
        print(f"   🎥 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ 视频生成成功: {output_video}")
            concat_file.unlink()  # 删除临时文件
            print(f"   📁 输出文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print(f"   ❌ ffmpeg 错误:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("   ❌ 错误：未找到 ffmpeg，请先安装 ffmpeg")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: 下载 https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='将 .sij 帧文件合并成视频',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法（默认 25 fps）
  python merge_video_frames.py raw_jpgs output.mp4
  
  # 指定帧率
  python merge_video_frames.py raw_jpgs output.mp4 --fps 30
  
  # 使用相对路径
  python merge_video_frames.py ./frames video.mp4 --fps 24
        """
    )
    
    parser.add_argument('frames_dir', help='包含 .sij 帧文件的目录')
    parser.add_argument('output_video', help='输出视频文件路径')
    parser.add_argument('--fps', type=int, default=25, help='视频帧率（默认: 25）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 视频帧合成工具")
    print("=" * 60)
    
    success = merge_frames_to_video(args.frames_dir, args.output_video, args.fps)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 视频合成完成！")
        print("=" * 60)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()


