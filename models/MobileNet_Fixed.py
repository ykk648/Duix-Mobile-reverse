"""PyTorch reproduction of the 160px DUIX NCNN talking-head model.

The layer/channel layout in this file is taken from the decrypted ``dh_model.p``
included with the v2.0.1 Leo model.  It intentionally keeps the public class
name ``MobileNetV2Unet`` used by the original examples.

NCNN's GroupNorm layers are represented by ``GroupNorm(1, C)``.  The exported
model is fully convolutional in the image path, but the released model is
trained and used with a 160x160 face crop.
"""

from __future__ import annotations

import torch
import torch.nn as nn


def _norm(channels: int, use_groupnorm: bool) -> nn.Module:
    return nn.GroupNorm(1, channels) if use_groupnorm else nn.BatchNorm2d(channels)


class ConvNormAct(nn.Module):
    """NCNN convolution with fused bias/ReLU; projection norm is separate."""

    def __init__(self, cin: int, cout: int, kernel_size: int, stride=1,
                 padding=0, *, groups: int = 1):
        super().__init__()
        self.conv = nn.Conv2d(cin, cout, kernel_size, stride, padding,
                              groups=groups, bias=True)
        self.act = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.conv(x))


class NcnnInvertedResidual(nn.Module):
    """MobileNetV2 block as used by the decrypted NCNN graph.

    NCNN stores the projection convolution, GroupNorm and ReLU as separate
    layers.  Keeping them separate also makes state-dict mapping predictable.
    """

    def __init__(self, cin: int, cout: int, stride: int, expand_ratio: int = 6,
                 *, use_groupnorm: bool = True):
        super().__init__()
        if stride not in (1, 2):
            raise ValueError("stride must be 1 or 2")
        hidden = cin * expand_ratio
        self.use_res_connect = stride == 1 and cin == cout

        layers: list[nn.Module] = []
        if expand_ratio != 1:
            layers.append(ConvNormAct(cin, hidden, 1))
        layers.append(ConvNormAct(hidden, hidden, 3, stride, 1, groups=hidden))
        if expand_ratio == 1:
            # The first 16-channel MobileNet block in dh_model.p is
            # depthwise-conv + biased 1x1 Conv+ReLU; it has no GroupNorm.
            layers.append(ConvNormAct(hidden, cout, 1))
        else:
            layers.extend([
                nn.Conv2d(hidden, cout, 1, 1, 0, bias=False),
                _norm(cout, use_groupnorm),
                nn.ReLU(inplace=True),
            ])
        self.block = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.block(x)
        return x + y if self.use_res_connect else y


class AudioEncoder(nn.Module):
    """The eight convolutional audio layers in ``dh_model.p``.

    NCNN's Mat layout is represented by PyTorch as ``[B, 1, 20, 256]``.
    The public API accepts the convenient ``[B, 256, 20]`` form and performs
    the required transpose.
    """

    def __init__(self, *, use_groupnorm: bool = True):
        super().__init__()
        self.conv1 = ConvNormAct(1, 16, 3, (1, 2), 0)
        self.conv2 = ConvNormAct(16, 32, 3, (1, 2), 0)
        # ``conv_2`` has no activation; NCNN adds it to the skip and then
        # applies ReLU (split -> convolution -> add -> ReLU).
        self.conv3 = nn.Conv2d(32, 32, 3, 1, 1, bias=True)
        self.conv4 = ConvNormAct(32, 64, 3, (1, 2), 1)
        self.conv5 = ConvNormAct(64, 128, 3, (1, 2), 1)
        self.conv6 = ConvNormAct(128, 128, 3, 2, 1)
        self.conv7 = ConvNormAct(128, 128, 3, 2, 2)
        self.conv8 = nn.Conv2d(128, 128, 3, 1, 1, bias=True)

    def forward(self, audio: torch.Tensor) -> torch.Tensor:
        if audio.ndim == 3:
            if audio.shape[1] != 256:
                raise ValueError(f"audio must be [B,256,T], got {tuple(audio.shape)}")
            audio = audio.transpose(1, 2).unsqueeze(1)
        elif audio.ndim == 4:
            if audio.shape[1] != 1 or audio.shape[3] != 256:
                raise ValueError(f"audio must be [B,1,20,256], got {tuple(audio.shape)}")
        else:
            raise ValueError(f"unsupported audio shape: {tuple(audio.shape)}")

        x = self.conv2(self.conv1(audio))
        x = torch.relu(self.conv3(x) + x)
        x = self.conv4(x)
        x = self.conv5(x)
        x = self.conv6(x)
        x = self.conv7(x)
        return torch.relu(self.conv8(x) + x)


class MobileNetV2Encoder(nn.Module):
    """Image encoder matching the padding and channel sequence in NCNN."""

    def __init__(self, *, use_groupnorm: bool = True):
        super().__init__()
        self.pad = nn.ZeroPad2d(1)
        self.stem = ConvNormAct(6, 16, 3, 1, 0)
        self.stem_down = ConvNormAct(16, 32, 3, 2, 1)

        # t, output channels, number of blocks, first-block stride
        settings = [(1, 16, 1, 1), (6, 24, 2, 2), (6, 32, 3, 2),
                    (6, 64, 4, 2), (6, 96, 3, 1), (6, 160, 3, 2),
                    (6, 320, 1, 1)]
        blocks: list[nn.Module] = []
        cin = 32
        for expansion, cout, count, stride in settings:
            for index in range(count):
                blocks.append(NcnnInvertedResidual(
                    cin, cout, stride if index == 0 else 1, expansion,
                    use_groupnorm=use_groupnorm))
                cin = cout
        self.blocks = nn.ModuleList(blocks)
        self.last = ConvNormAct(320, 320, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, ...]:
        x = self.stem_down(self.stem(self.pad(x)))
        feature_by_channel: dict[int, torch.Tensor] = {}
        for block in self.blocks:
            x = block(x)
            # Keep the final tensor at each skip channel.  The graph uses:
            # Skip blobs 23, 38, 61, 113: 16@80, 24@40, 32@20, 96@10.
            if x.shape[1] in (16, 24, 32, 96):
                feature_by_channel[x.shape[1]] = x
        x = self.last(x)
        return (feature_by_channel[16], feature_by_channel[24],
                feature_by_channel[32], feature_by_channel[96], x)


class MobileNetV2Unet(nn.Module):
    """DUIX v2.0.1 160px model.

    ``forward`` follows the original Python reproduction convention:
    ``model(face, audio)``.  ``face`` is ``[B,6,160,160]`` and ``audio`` is
    ``[B,256,20]``.  The released NCNN graph directly produces a 5x5 audio
    feature map, so no resize/pooling is performed.
    """

    def __init__(self, *, use_groupnorm: bool = True, **_: object):
        super().__init__()
        self.audio_encoder = AudioEncoder(use_groupnorm=use_groupnorm)
        self.backbone = MobileNetV2Encoder(use_groupnorm=use_groupnorm)

        # Exact decoder channel sizes from cat_0..cat_4 in dh_model.p.
        self.dconv0 = nn.ConvTranspose2d(128, 320, 1, 1, 0)
        self.invres0 = NcnnInvertedResidual(640, 320, 1, 6,
                                            use_groupnorm=use_groupnorm)
        self.dconv1 = nn.ConvTranspose2d(320, 160, 3, 2, 1, output_padding=1)
        self.invres1 = NcnnInvertedResidual(256, 128, 1, 6,
                                            use_groupnorm=use_groupnorm)
        self.dconv2 = nn.ConvTranspose2d(128, 64, 3, 2, 1, output_padding=1)
        self.invres2 = NcnnInvertedResidual(96, 48, 1, 6,
                                            use_groupnorm=use_groupnorm)
        self.dconv3 = nn.ConvTranspose2d(48, 24, 3, 2, 1, output_padding=1)
        self.invres3 = NcnnInvertedResidual(48, 24, 1, 6,
                                            use_groupnorm=use_groupnorm)
        self.dconv4 = nn.ConvTranspose2d(24, 16, 3, 2, 1, output_padding=1)
        self.invres4 = NcnnInvertedResidual(32, 16, 1, 6,
                                            use_groupnorm=use_groupnorm)
        self.dconv5 = nn.ConvTranspose2d(16, 8, 3, 2, 1, output_padding=1)
        self.output_pad = nn.ZeroPad2d(1)
        self.output_conv = nn.Conv2d(8, 3, 3, 1, 0)

        self._initialize_weights()

    @staticmethod
    def _initialize_weights() -> None:
        # Kept as a named hook for compatibility; PyTorch defaults are valid
        # for inference and loading an NCNN-converted state dict.
        return None

    def forward(self, face: torch.Tensor, audio: torch.Tensor) -> torch.Tensor:
        if face.ndim != 4 or face.shape[1] != 6:
            raise ValueError(f"face must be [B,6,H,W], got {tuple(face.shape)}")
        audio_feature = self.audio_encoder(audio)
        skips = self.backbone(face)
        x1, x2, x3, x4, x5 = skips

        if audio_feature.shape[-2:] != x5.shape[-2:]:
            raise RuntimeError(
                f"audio/image bottleneck mismatch: {audio_feature.shape[-2:]} vs {x5.shape[-2:]}")

        x = self.invres0(torch.cat([x5, self.dconv0(audio_feature)], dim=1))
        x = self.invres1(torch.cat([x4, self.dconv1(x)], dim=1))
        x = self.invres2(torch.cat([x3, self.dconv2(x)], dim=1))
        x = self.invres3(torch.cat([x2, self.dconv3(x)], dim=1))
        x = self.invres4(torch.cat([x1, self.dconv4(x)], dim=1))
        x = self.dconv5(x)
        return torch.tanh(self.output_conv(self.output_pad(x)))


def test_model() -> None:
    model = MobileNetV2Unet().eval()
    face = torch.randn(1, 6, 160, 160)
    audio = torch.randn(1, 256, 20)
    with torch.no_grad():
        output = model(face, audio)
    params = sum(p.numel() for p in model.parameters())
    print(f"face={tuple(face.shape)} audio={tuple(audio.shape)} output={tuple(output.shape)}")
    print(f"params={params:,} range=({output.min().item():.3f},{output.max().item():.3f})")


if __name__ == "__main__":
    test_model()
