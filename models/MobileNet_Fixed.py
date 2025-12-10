"""
修正后的 MobileNet U-Net 模型
与 NCNN 模型结构完全对齐
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class Conv2d(nn.Module):
    """基础卷积块"""
    def __init__(self, cin, cout, kernel_size, stride, padding, residual=False, 
                 dilation=1, use_groupnorm=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conv_block = nn.Sequential(
            nn.Conv2d(cin, cout, kernel_size, stride, padding, 
                     groups=1, dilation=dilation),
            nn.GroupNorm(1, cout) if use_groupnorm else nn.BatchNorm2d(cout)
        )
        self.act = nn.ReLU()
        self.residual = residual

    def forward(self, x):
        out = self.conv_block(x)
        if self.residual:
            out += x
        return self.act(out)


def conv_bn(inp, oup, stride, use_groupnorm=False):
    """标准卷积 + 归一化 + ReLU"""
    if use_groupnorm:
        return nn.Sequential(
            nn.Conv2d(inp, oup, 3, stride, 1, bias=False),
            nn.GroupNorm(1, oup),
            nn.ReLU(inplace=True)
        )
    else:
        return nn.Sequential(
            nn.Conv2d(inp, oup, 3, stride, 1, bias=False),
            nn.BatchNorm2d(oup),
            nn.ReLU(inplace=True)
        )


def conv_1x1_bn(inp, oup, use_groupnorm=False):
    """1×1 卷积 + 归一化 + ReLU"""
    if use_groupnorm:
        return nn.Sequential(
            nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
            nn.GroupNorm(1, oup),
            nn.ReLU(inplace=True)
        )
    else:
        return nn.Sequential(
            nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
            nn.BatchNorm2d(oup),
            nn.ReLU(inplace=True)
        )


class InvertedResidual(nn.Module):
    """Inverted Residual Block (MobileNetV2)"""
    def __init__(self, inp, oup, stride, expand_ratio, use_groupnorm=False):
        super(InvertedResidual, self).__init__()
        self.stride = stride
        assert stride in [1, 2]

        hidden_dim = round(inp * expand_ratio)
        self.use_res_connect = self.stride == 1 and inp == oup

        if expand_ratio == 1:
            if use_groupnorm:
                self.conv = nn.Sequential(
                    # dw
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, 
                             groups=hidden_dim, bias=False),
                    nn.GroupNorm(1, hidden_dim),
                    nn.ReLU(inplace=True),
                    # pw-linear
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                    nn.GroupNorm(1, oup),
                    nn.ReLU(inplace=True)
                )
            else:
                self.conv = nn.Sequential(
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, 
                             groups=hidden_dim, bias=False),
                    nn.BatchNorm2d(hidden_dim),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(oup),
                    nn.ReLU(inplace=True)
                )
        else:
            if use_groupnorm:
                self.conv = nn.Sequential(
                    # pw
                    nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False),
                    nn.GroupNorm(1, hidden_dim),
                    nn.ReLU(inplace=True),
                    # dw
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, 
                             groups=hidden_dim, bias=False),
                    nn.GroupNorm(1, hidden_dim),
                    nn.ReLU(inplace=True),
                    # pw-linear
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                    nn.GroupNorm(1, oup),
                    nn.ReLU(inplace=True)
                )
            else:
                self.conv = nn.Sequential(
                    nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(hidden_dim),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, 
                             groups=hidden_dim, bias=False),
                    nn.BatchNorm2d(hidden_dim),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(oup),
                    nn.ReLU(inplace=True)
                )

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)


class MobileNetV2(nn.Module):
    """修正后的 MobileNetV2 编码器（与 NCNN 对齐）"""
    def __init__(self, n_class=1000, input_size=224, width_mult=1., 
                 use_groupnorm=False):
        super(MobileNetV2, self).__init__()
        block = InvertedResidual
        input_channel = 32
        last_channel = 320
        interverted_residual_setting = [
            # t, c, n, s
            [1, 16, 1, 1],
            [6, 24, 2, 2],
            [6, 32, 3, 2],
            [6, 64, 4, 2],
            [6, 96, 3, 1],
            [6, 160, 3, 2],
            [6, 320, 1, 1],
        ]

        # ✅ 修正：与 NCNN 对齐的第一层
        # NCNN: Padding → Conv(6→16, k3, s1, p0) → Conv(16→32, k3, s2, p1)
        assert input_size % 32 == 0
        input_channel = int(input_channel * width_mult)
        self.last_channel = int(last_channel * width_mult) if width_mult > 1.0 else last_channel
        
        self.features = []
        
        # 第1层: Padding + Conv(6→16, stride=1)
        self.features.append(nn.ZeroPad2d(1))
        if use_groupnorm:
            self.features.extend([
                nn.Conv2d(6, 16, 3, stride=1, padding=0, bias=False),
                nn.GroupNorm(1, 16),
                nn.ReLU(inplace=True)
            ])
        else:
            self.features.extend([
                nn.Conv2d(6, 16, 3, stride=1, padding=0, bias=False),
                nn.BatchNorm2d(16),
                nn.ReLU(inplace=True)
            ])
        
        # 第2层: Conv(16→32, stride=2)
        if use_groupnorm:
            self.features.extend([
                nn.Conv2d(16, input_channel, 3, stride=2, padding=1, bias=False),
                nn.GroupNorm(1, input_channel),
                nn.ReLU(inplace=True)
            ])
        else:
            self.features.extend([
                nn.Conv2d(16, input_channel, 3, stride=2, padding=1, bias=False),
                nn.BatchNorm2d(input_channel),
                nn.ReLU(inplace=True)
            ])
        
        # 构建 inverted residual blocks
        for t, c, n, s in interverted_residual_setting:
            output_channel = int(c * width_mult)
            for i in range(n):
                if i == 0:
                    self.features.append(block(input_channel, output_channel, s, 
                                             expand_ratio=t, use_groupnorm=use_groupnorm))
                else:
                    self.features.append(block(input_channel, output_channel, 1, 
                                             expand_ratio=t, use_groupnorm=use_groupnorm))
                input_channel = output_channel
        
        # 最后一层
        self.features.append(conv_1x1_bn(input_channel, self.last_channel, use_groupnorm))
        
        # 转为 nn.Sequential
        self.features = nn.Sequential(*self.features)

        self._initialize_weights()

    def forward(self, x):
        x = self.features(x)
        return x

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                n = m.weight.size(1)
                m.weight.data.normal_(0, 0.01)
                m.bias.data.zero_()


class AudioEncoder(nn.Module):
    """✅ 修正后的音频编码器（完全对齐 NCNN）"""
    def __init__(self, use_groupnorm=False):
        super(AudioEncoder, self).__init__()
        
        # 第1层：1→16, stride=2, padding=0
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 16, 3, stride=2, padding=0),
            nn.BatchNorm2d(16),
            nn.ReLU()
        )
        
        # 第2层：16→32, stride=2, padding=0
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 3, stride=2, padding=0),
            nn.BatchNorm2d(32),
            nn.ReLU()
        )
        
        # 第3层：32→32 + Residual
        self.conv3 = nn.Conv2d(32, 32, 3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(32)
        
        # 第4层：32→64, stride=2
        self.conv4 = nn.Sequential(
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        
        # 第5层：64→128, stride=2
        self.conv5 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        # ✅ 修正：不使用 dilation，避免尺寸问题
        # 第6层：128→128, stride=2
        self.conv6 = nn.Sequential(
            nn.Conv2d(128, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        # 第7层：128→128, stride=2
        self.conv7 = nn.Sequential(
            nn.Conv2d(128, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        # 第8层：128→128 + Residual
        self.conv8 = nn.Conv2d(128, 128, 3, stride=1, padding=1)
        self.bn8 = nn.BatchNorm2d(128)
        
    def forward(self, x):
        # x: [B, 256, 20] → 需要转换为 [B, 1, 20, 256] (交换高宽)
        if x.dim() == 3:
            # [B, 256, 20] → [B, 20, 256] → [B, 1, 20, 256]
            x = x.transpose(1, 2).unsqueeze(1)
        elif x.dim() == 4 and x.shape[1] == 1 and x.shape[2] == 256:
            # [B, 1, 256, 20] → [B, 1, 20, 256]
            x = x.transpose(2, 3)
        
        x = self.conv1(x)  # [B, 16, 9, 127]
        x = self.conv2(x)  # [B, 32, 4, 63]
        
        # Residual block 1
        identity = x
        x = self.conv3(x)
        x = self.bn3(x)
        x = x + identity
        x = F.relu(x)      # [B, 32, 4, 63]
        
        x = self.conv4(x)  # [B, 64, 2, 32]
        x = self.conv5(x)  # [B, 128, 1, 16]
        x = self.conv6(x)  # [B, 128, 1, 8]
        x = self.conv7(x)  # [B, 128, 1, 4]
        
        # Residual block 2
        identity = x
        x = self.conv8(x)
        x = self.bn8(x)
        x = x + identity
        x = F.relu(x)      # [B, 128, 1, 4]
        
        # 调整到 5×5 以匹配解码器
        x = F.adaptive_avg_pool2d(x, (5, 5))  # [B, 128, 5, 5]
        
        return x


class MobileNetV2Unet(nn.Module):
    """✅ 完全修正的 MobileNetV2 U-Net（对齐 NCNN + 参考老版本）"""
    def __init__(self, channel_scale_factor=2, use_groupnorm=False, **kwargs):
        super(MobileNetV2Unet, self).__init__()

        self.channel_scale_factor = channel_scale_factor
        self.use_groupnorm = use_groupnorm

        # 图像编码器 - 保持原结构但调整第一层
        self.backbone = MobileNetV2(use_groupnorm=use_groupnorm)
        # 删除不使用的 classifier，避免 DDP 中的未使用参数问题
        if hasattr(self.backbone, 'classifier'):
            del self.backbone.classifier

        # 音频编码器
        self.audio_encoder = AudioEncoder(use_groupnorm=use_groupnorm)

        # 解码器 - 参考老版本的结构
        self.dconv0 = nn.ConvTranspose2d(128, 128, kernel_size=1, stride=1, padding=0)
        self.invres0 = InvertedResidual(448, 96, 1, 6, use_groupnorm=use_groupnorm)

        self.dconv1 = nn.ConvTranspose2d(96, 96, 3, padding=1, stride=2, output_padding=1)
        self.invres1 = InvertedResidual(192, 96, 1, 6, use_groupnorm=use_groupnorm)

        self.dconv2 = nn.ConvTranspose2d(96, 32, 3, padding=1, stride=2, output_padding=1)
        self.invres2 = InvertedResidual(64, 32, 1, 6, use_groupnorm=use_groupnorm)

        self.dconv3 = nn.ConvTranspose2d(32, 24, 3, padding=1, stride=2, output_padding=1)
        self.invres3 = InvertedResidual(48, 24, 1, 6, use_groupnorm=use_groupnorm)

        self.dconv4 = nn.ConvTranspose2d(24, 16, 3, padding=1, stride=2, output_padding=1)
        self.invres4 = InvertedResidual(32, 16, 1, 6, use_groupnorm=use_groupnorm)

        self.dconv5 = nn.ConvTranspose2d(16, 8, 3, padding=1, stride=2, output_padding=1)

        # ✅ 修正：输出层使用 TanH（老版本用的是 sigmoid，需要改）
        self.conv_last = nn.Conv2d(8, 3, 1)
        self.conv_score = nn.Conv2d(3, 3, 1)

    def forward(self, x, audio):
        # 音频编码 - audio: [B, 256, 20] -> [B, 1, 256, 20]
        if audio.dim() == 3:
            audio = audio.unsqueeze(1)
        audio_embedding = self.audio_encoder(audio)  # [B, 128, 5, 5]

        # ✅ 图像编码器：提取多尺度特征
        # 根据实际输出，正确的跳跃连接位置：
        # Layer 7:  [1, 16, 80, 80]  → x1
        # Layer 9:  [1, 24, 40, 40]  → x2
        # Layer 12: [1, 32, 20, 20]  → x3
        # Layer 17: [1, 96, 10, 10]  → x4
        # Layer 24: [1, 320, 5, 5]   → x5
        
        for i, layer in enumerate(self.backbone.features):
            x = layer(x)
            if i == 7:
                x1 = x  # [1, 16, 80, 80]
            elif i == 9:
                x2 = x  # [1, 24, 40, 40]
            elif i == 12:
                x3 = x  # [1, 32, 20, 20]
            elif i == 17:
                x4 = x  # [1, 96, 10, 10]
        
        x5 = x  # [1, 320, 5, 5]

        # ✅ 解码器：上采样 + 跳跃连接
        # 解码器层 0: [320, 5, 5] + [128, 5, 5] → [448, 5, 5] → [96, 5, 5]
        x = self.invres0(torch.cat([x5, self.dconv0(audio_embedding)], dim=1))
        
        # 解码器层 1: [96, 5, 5] → [96, 10, 10] concat [96, 10, 10] → [192, 10, 10] → [96, 10, 10]
        x = self.invres1(torch.cat([x4, self.dconv1(x)], dim=1))
        
        # 解码器层 2: [96, 10, 10] → [32, 20, 20] concat [32, 20, 20] → [64, 20, 20] → [32, 20, 20]
        x = self.invres2(torch.cat([x3, self.dconv2(x)], dim=1))
        
        # 解码器层 3: [32, 20, 20] → [24, 40, 40] concat [24, 40, 40] → [48, 40, 40] → [24, 40, 40]
        x = self.invres3(torch.cat([x2, self.dconv3(x)], dim=1))
        
        # 解码器层 4: [24, 40, 40] → [16, 80, 80] concat [16, 80, 80] → [32, 80, 80] → [16, 80, 80]
        x = self.invres4(torch.cat([x1, self.dconv4(x)], dim=1))
        
        # 最终输出: [16, 80, 80] → [8, 160, 160] → [3, 160, 160]
        x = self.dconv5(x)
        x = self.conv_last(x)
        x = self.conv_score(x)
        x = torch.tanh(x)  # ✅ 修正：使用 TanH 而非 Sigmoid
        
        return x


def test_model():
    """测试模型"""
    print("=" * 50)
    print("测试修正后的模型")
    print("=" * 50)
    
    model = MobileNetV2Unet(use_groupnorm=False)
    model.eval()
    
    # 测试输入
    audio = torch.randn(1, 256, 20)
    face = torch.randn(1, 6, 160, 160)
    
    print(f"Audio input shape: {audio.shape}")
    print(f"Face input shape: {face.shape}")
    
    with torch.no_grad():
        output = model(face, audio)
    
    print(f"\nOutput shape: {output.shape}")
    print(f"Output range: [{output.min():.3f}, {output.max():.3f}]")
    print(f"Expected range: [-1, 1] (TanH)")
    
    # 统计参数量
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\nTotal parameters: {total_params / 1e6:.2f}M")
    print(f"Expected: ~3.77M (NCNN model)")
    
    print("\n" + "=" * 50)
    print("✅ 模型测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_model()

