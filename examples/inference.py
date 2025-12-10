"""
DUIX 模型推理示例

使用 PyTorch 复现的模型进行推理
"""

import sys
import os

# 添加 models 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

import torch
import torch.nn.functional as F
import numpy as np

try:
    from MobileNet_Fixed import MobileNetV2Unet
except ImportError:
    print("请确保 models/MobileNet_Fixed.py 存在")
    sys.exit(1)


def create_model(use_gpu=True, use_groupnorm=False):
    """创建模型"""
    model = MobileNetV2Unet(use_groupnorm=use_groupnorm)
    model.eval()
    
    if use_gpu and torch.cuda.is_available():
        model = model.cuda()
        print(f"使用 GPU: {torch.cuda.get_device_name()}")
    else:
        print("使用 CPU")
    
    return model


def preprocess_audio(audio_features):
    """
    预处理音频特征
    
    Args:
        audio_features: numpy array, shape [T, 256] 或 [256, T]
    
    Returns:
        torch.Tensor, shape [1, 256, 20]
    """
    if isinstance(audio_features, np.ndarray):
        audio_features = torch.from_numpy(audio_features).float()
    
    # 确保形状是 [256, T]
    if audio_features.shape[0] != 256:
        audio_features = audio_features.T
    
    # 截取或填充到 20 帧
    T = audio_features.shape[1]
    if T < 20:
        # 填充
        pad = torch.zeros(256, 20 - T)
        audio_features = torch.cat([audio_features, pad], dim=1)
    elif T > 20:
        # 截取
        audio_features = audio_features[:, :20]
    
    # 添加 batch 维度
    return audio_features.unsqueeze(0)  # [1, 256, 20]


def preprocess_face(current_frame, reference_frame):
    """
    预处理人脸图像
    
    Args:
        current_frame: numpy array, shape [H, W, 3], uint8 [0-255]
        reference_frame: numpy array, shape [H, W, 3], uint8 [0-255]
    
    Returns:
        torch.Tensor, shape [1, 6, H, W]
    """
    # 转换为 tensor
    if isinstance(current_frame, np.ndarray):
        current_frame = torch.from_numpy(current_frame).float()
    if isinstance(reference_frame, np.ndarray):
        reference_frame = torch.from_numpy(reference_frame).float()
    
    # 归一化到 [-1, 1]
    current_frame = (current_frame / 255.0) * 2 - 1
    reference_frame = (reference_frame / 255.0) * 2 - 1
    
    # [H, W, 3] -> [3, H, W]
    current_frame = current_frame.permute(2, 0, 1)
    reference_frame = reference_frame.permute(2, 0, 1)
    
    # 合并通道
    face = torch.cat([current_frame, reference_frame], dim=0)  # [6, H, W]
    
    # 调整大小到 160x160
    face = F.interpolate(face.unsqueeze(0), size=(160, 160), mode='bilinear', align_corners=False)
    
    return face  # [1, 6, 160, 160]


def postprocess_output(output):
    """
    后处理模型输出
    
    Args:
        output: torch.Tensor, shape [1, 3, H, W], range [-1, 1]
    
    Returns:
        numpy array, shape [H, W, 3], uint8 [0-255]
    """
    # [-1, 1] -> [0, 255]
    output = (output + 1) / 2 * 255
    output = output.clamp(0, 255)
    
    # [1, 3, H, W] -> [H, W, 3]
    output = output[0].permute(1, 2, 0)
    
    # 转换为 numpy
    output = output.cpu().numpy().astype(np.uint8)
    
    return output


@torch.no_grad()
def inference(model, audio, face, device='cuda'):
    """
    模型推理
    
    Args:
        model: MobileNetV2Unet 模型
        audio: torch.Tensor, shape [B, 256, 20]
        face: torch.Tensor, shape [B, 6, H, W]
        device: 'cuda' 或 'cpu'
    
    Returns:
        torch.Tensor, shape [B, 3, H, W], range [-1, 1]
    """
    # 移动到设备
    audio = audio.to(device)
    face = face.to(device)
    
    # 推理
    output = model(face, audio)
    
    return output


def demo_random_input():
    """使用随机输入演示"""
    print("=" * 60)
    print("DUIX 模型推理演示 - 随机输入")
    print("=" * 60)
    
    # 创建模型
    use_gpu = torch.cuda.is_available()
    model = create_model(use_gpu=use_gpu)
    device = 'cuda' if use_gpu else 'cpu'
    
    # 生成随机输入
    batch_size = 2
    audio = torch.randn(batch_size, 256, 20)
    face = torch.randn(batch_size, 6, 160, 160)
    
    print(f"\n输入:")
    print(f"  Audio: {audio.shape}")
    print(f"  Face:  {face.shape}")
    
    # 推理
    output = inference(model, audio, face, device)
    
    print(f"\n输出:")
    print(f"  Shape: {output.shape}")
    print(f"  Range: [{output.min():.3f}, {output.max():.3f}]")
    print(f"  Mean:  {output.mean():.3f}")
    print(f"  Std:   {output.std():.3f}")
    
    # 后处理
    for i in range(batch_size):
        result = postprocess_output(output[i:i+1])
        print(f"\n  结果 {i+1}: shape={result.shape}, dtype={result.dtype}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    print("=" * 60)


def demo_image_input():
    """使用图像输入演示（模拟）"""
    print("=" * 60)
    print("DUIX 模型推理演示 - 图像输入（模拟）")
    print("=" * 60)
    
    # 创建模型
    use_gpu = torch.cuda.is_available()
    model = create_model(use_gpu=use_gpu)
    device = 'cuda' if use_gpu else 'cpu'
    
    # 模拟图像输入 (实际应从文件读取)
    current_frame = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    reference_frame = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    
    # 模拟音频特征 (实际应从 Wenet 等提取)
    audio_features = np.random.randn(256, 20).astype(np.float32)
    
    print(f"\n原始输入:")
    print(f"  Current frame:   {current_frame.shape}, dtype={current_frame.dtype}")
    print(f"  Reference frame: {reference_frame.shape}, dtype={reference_frame.dtype}")
    print(f"  Audio features:  {audio_features.shape}, dtype={audio_features.dtype}")
    
    # 预处理
    audio = preprocess_audio(audio_features).to(device)
    face = preprocess_face(current_frame, reference_frame).to(device)
    
    print(f"\n预处理后:")
    print(f"  Audio: {audio.shape}")
    print(f"  Face:  {face.shape}")
    
    # 推理
    output = inference(model, audio, face, device)
    
    print(f"\n模型输出:")
    print(f"  Shape: {output.shape}")
    print(f"  Range: [{output.min():.3f}, {output.max():.3f}]")
    
    # 后处理
    result = postprocess_output(output)
    print(f"\n最终结果:")
    print(f"  Shape: {result.shape}")
    print(f"  Dtype: {result.dtype}")
    print(f"  Range: [{result.min()}, {result.max()}]")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    print("=" * 60)


def benchmark(num_iterations=100):
    """性能测试"""
    import time
    
    print("=" * 60)
    print("DUIX 模型性能测试")
    print("=" * 60)
    
    # 创建模型
    use_gpu = torch.cuda.is_available()
    model = create_model(use_gpu=use_gpu)
    device = 'cuda' if use_gpu else 'cpu'
    
    # 准备输入
    audio = torch.randn(1, 256, 20).to(device)
    face = torch.randn(1, 6, 160, 160).to(device)
    
    # 预热
    print("\n预热...")
    for _ in range(10):
        _ = model(face, audio)
    
    if use_gpu:
        torch.cuda.synchronize()
    
    # 测试
    print(f"测试 {num_iterations} 次推理...")
    times = []
    
    for _ in range(num_iterations):
        start = time.perf_counter()
        _ = model(face, audio)
        if use_gpu:
            torch.cuda.synchronize()
        times.append(time.perf_counter() - start)
    
    times = np.array(times) * 1000  # 转换为毫秒
    
    print(f"\n结果:")
    print(f"  平均耗时: {times.mean():.2f} ms")
    print(f"  最小耗时: {times.min():.2f} ms")
    print(f"  最大耗时: {times.max():.2f} ms")
    print(f"  标准差:   {times.std():.2f} ms")
    print(f"  FPS:      {1000 / times.mean():.1f}")
    
    print("\n" + "=" * 60)
    print("✅ 性能测试完成")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DUIX 模型推理示例')
    parser.add_argument('--mode', type=str, default='random',
                       choices=['random', 'image', 'benchmark'],
                       help='运行模式: random(随机输入), image(图像输入), benchmark(性能测试)')
    parser.add_argument('--iterations', type=int, default=100,
                       help='性能测试迭代次数')
    
    args = parser.parse_args()
    
    if args.mode == 'random':
        demo_random_input()
    elif args.mode == 'image':
        demo_image_input()
    elif args.mode == 'benchmark':
        benchmark(args.iterations)

