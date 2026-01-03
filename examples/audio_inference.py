#!/usr/bin/env python3
"""
音频特征提取推理示例

完整的音频到特征向量推理流程：
1. 加载音频文件（WAV/PCM）
2. 提取 MFCC 特征
3. WeNet ONNX 推理
4. 输出 BNF 特征向量

依赖：
    pip install onnxruntime numpy librosa soundfile
"""

import numpy as np
import onnxruntime as ort
import librosa
import soundfile as sf
import sys
import os
from pathlib import Path

class WeNetInference:
    """WeNet 音频特征提取推理类"""
    
    def __init__(self, model_path, melcnt=321, bnfcnt=79, num_threads=2):
        """
        初始化 WeNet ONNX 推理引擎
        
        Args:
            model_path: WeNet ONNX 模型文件路径
            melcnt: Mel 特征帧数（默认 321）
            bnfcnt: BNF 特征帧数（默认 79）
            num_threads: ONNX Runtime 线程数（默认 2）
        """
        self.melcnt = melcnt
        self.bnfcnt = bnfcnt
        
        # 初始化 ONNX Runtime
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = num_threads
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.add_session_config_entry("session.disable_prepacking", "1")
        
        # 加载模型
        print(f"📥 加载 WeNet 模型: {model_path}")
        self.session = ort.InferenceSession(
            model_path,
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        
        # 获取输入输出信息
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]
        
        print(f"✅ 模型加载成功")
        print(f"   输入: {self.input_names}")
        print(f"   输出: {self.output_names}")
        
        # 验证输入输出形状
        input_shapes = {inp.name: inp.shape for inp in self.session.get_inputs()}
        output_shapes = {out.name: out.shape for out in self.session.get_outputs()}
        print(f"   输入形状: {input_shapes}")
        print(f"   输出形状: {output_shapes}")
    
    def extract_mfcc(self, audio_data, sample_rate=16000, n_mels=80, hop_length=160):
        """
        提取 MFCC 特征（Mel 频谱）
        
        Args:
            audio_data: 音频数据（numpy array，float32）
            sample_rate: 采样率（默认 16000 Hz）
            n_mels: Mel 滤波器数量（默认 80）
            hop_length: 帧移（默认 160，对应 10ms）
        
        Returns:
            mel_features: Mel 频谱特征 [melcnt, 80]
        """
        # 确保音频是 float32 格式
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # 归一化到 [-1, 1]
        if audio_data.max() > 1.0 or audio_data.min() < -1.0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        # 提取 Mel 频谱特征
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data,
            sr=sample_rate,
            n_mels=n_mels,
            hop_length=hop_length,
            n_fft=512,
            fmin=0,
            fmax=8000
        )
        
        # 转换为对数尺度
        mel_log = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 归一化到 [0, 1] 或 [-1, 1]
        mel_log = (mel_log - mel_log.min()) / (mel_log.max() - mel_log.min() + 1e-8)
        
        # 转置：从 [n_mels, time] 转为 [time, n_mels]
        mel_features = mel_log.T
        
        return mel_features
    
    def pad_or_truncate_mel(self, mel_features, target_length):
        """
        填充或截断 Mel 特征到目标长度
        
        Args:
            mel_features: Mel 特征 [time, 80]
            target_length: 目标长度（melcnt）
        
        Returns:
            padded_mel: 处理后的 Mel 特征 [target_length, 80]
        """
        current_length = mel_features.shape[0]
        
        if current_length < target_length:
            # 填充零
            pad_length = target_length - current_length
            pad = np.zeros((pad_length, 80), dtype=np.float32)
            padded_mel = np.concatenate([mel_features, pad], axis=0)
        elif current_length > target_length:
            # 截断
            padded_mel = mel_features[:target_length]
        else:
            padded_mel = mel_features
        
        return padded_mel
    
    def infer(self, mel_features):
        """
        执行 WeNet ONNX 推理
        
        Args:
            mel_features: Mel 频谱特征 [melcnt, 80]
        
        Returns:
            bnf_features: BNF 特征向量 [bnfcnt, 256]
        """
        # 确保形状正确
        if mel_features.shape[0] != self.melcnt:
            mel_features = self.pad_or_truncate_mel(mel_features, self.melcnt)
        
        # 准备输入
        # speech: [1, melcnt, 80]
        speech_input = mel_features.reshape(1, self.melcnt, 80).astype(np.float32)
        
        # speech_lengths: [1]
        speech_lengths = np.array([self.melcnt], dtype=np.int32)
        
        # 创建输入字典
        inputs = {
            self.input_names[0]: speech_input,      # speech
            self.input_names[1]: speech_lengths     # speech_lengths
        }
        
        # 执行推理
        outputs = self.session.run(self.output_names, inputs)
        
        # 获取输出（encoder_out）
        bnf_features = outputs[0]  # [1, bnfcnt, 256]
        
        # 移除 batch 维度
        bnf_features = bnf_features[0]  # [bnfcnt, 256]
        
        return bnf_features
    
    def process_audio_file(self, audio_path):
        """
        处理音频文件，返回 BNF 特征
        
        Args:
            audio_path: 音频文件路径（WAV/PCM）
        
        Returns:
            bnf_features: BNF 特征向量 [bnfcnt, 256]
        """
        print(f"\n📻 处理音频文件: {audio_path}")
        
        # 加载音频
        try:
            audio_data, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
            print(f"   采样率: {sample_rate} Hz")
            print(f"   时长: {len(audio_data) / sample_rate:.2f} 秒")
            print(f"   样本数: {len(audio_data):,}")
        except Exception as e:
            print(f"❌ 加载音频文件失败: {e}")
            return None
        
        # 提取 MFCC 特征
        print("🔍 提取 MFCC 特征...")
        mel_features = self.extract_mfcc(audio_data, sample_rate)
        print(f"   Mel 特征形状: {mel_features.shape}")
        
        # 填充或截断到目标长度
        mel_features = self.pad_or_truncate_mel(mel_features, self.melcnt)
        print(f"   处理后 Mel 特征形状: {mel_features.shape}")
        
        # WeNet 推理
        print("🧠 WeNet ONNX 推理...")
        bnf_features = self.infer(mel_features)
        print(f"   BNF 特征形状: {bnf_features.shape}")
        print(f"   BNF 特征范围: [{bnf_features.min():.4f}, {bnf_features.max():.4f}]")
        
        return bnf_features


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python audio_inference.py <wenet.onnx> <audio.wav> [输出.npy]")
        print("\n示例:")
        print("  python audio_inference.py wenet.onnx audio.wav")
        print("  python audio_inference.py wenet.onnx audio.wav output_bnf.npy")
        sys.exit(1)
    
    model_path = sys.argv[1]
    audio_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        sys.exit(1)
    
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎤 WeNet 音频特征提取推理")
    print("=" * 60)
    
    # 创建推理引擎
    try:
        wenet = WeNetInference(model_path, melcnt=321, bnfcnt=79)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    
    # 处理音频
    try:
        bnf_features = wenet.process_audio_file(audio_path)
        
        if bnf_features is not None:
            print("\n✅ 推理成功！")
            print(f"📊 BNF 特征统计:")
            print(f"   形状: {bnf_features.shape}")
            print(f"   均值: {bnf_features.mean():.4f}")
            print(f"   标准差: {bnf_features.std():.4f}")
            print(f"   最小值: {bnf_features.min():.4f}")
            print(f"   最大值: {bnf_features.max():.4f}")
            
            # 保存结果
            if output_path:
                np.save(output_path, bnf_features)
                print(f"\n💾 特征已保存到: {output_path}")
            else:
                # 默认输出文件名
                default_output = Path(audio_path).stem + "_bnf.npy"
                np.save(default_output, bnf_features)
                print(f"\n💾 特征已保存到: {default_output}")
        else:
            print("\n❌ 推理失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

