# Duix-Mobile release model catalog

本目录按官方 GitHub Releases 的模型包整理。`dh_model.p` 已解密并比较过：

## 165 层新版（可共用 PyTorch 结构/参数转换器）

这些包的解密 `dh_model.p` 完全相同：

```text
SHA256: 999d0c996521e2cbc4d758d6d16fe563e188f696ff541711f45dfa49fc6b1816
165 layers / 181 blobs
Convolution 55, ConvolutionDepthWise 22, Deconvolution 6
GroupNorm 21, Padding 2, TanH 1
```

| Release | 包/人物 | 压缩包 |
|---|---|---|
| v2.0.1 | Emma | `download/Emma.zip` |
| v2.0.1 | Kai | `download/Kai.zip` |
| v2.0.1 | Leo | `download/Leo.zip` |
| v2.0.1 | Lily | `download/Lily.zip` |
| v2.0.1 | Oliver | `download/Oliver.zip` |
| v2.0.1 | Sofia | `download/Sofia.zip` |
| v2.0.0 | 712880634105925 | `download/712880634105925_68b3f5a2208cc7438194d9d35fb0d5eb_optim_m80.zip` |
| v2.0.0 | 713276017438789 | `download/713276017438789_23737a8bb6c21137dbdba34ca75b9365_optim_m80.zip` |
| v2.0.0 | 713276132638789 | `download/713276132638789_505586d97c3e935299f57c6262d9ece7_optim_m80.zip` |
| v2.0.0 | 713557460262982 | `download/713557460262982_2457fffb22e79c764c9b47d66f50c507.zip` |
| v1.0.0 | aixia_2026_08_21 | `download/aixia_2026_08_21.zip` |
| v1.0.0 | ddzh | `download/ddzh.zip` |

这些模型的权重内容不同，但可以按同一层序列做 NCNN→PyTorch 转换或参数平均。

## 过渡/旧版结构（不要与 165 层模型混合平均）

| Release | 包/人物 | 结构 | 说明 |
|---|---|---:|---|
| v1.0.0 | bendi3_20240518 | 120 层 / 136 blobs | 过渡版；无新版 GroupNorm/Padding |
| v1.0.0 | airuike_20240409 | 121 层 / 137 blobs | 旧版 decoder；无新版 GroupNorm/Padding |

这两个包不能与 165 层模型直接做参数平均。

## 资源包（不是新的网络结构）

官方 release 还包含 demo 视频、APK、视频资源和测试资源包；它们不应放入模型平均池：

- `demo.mp4`
- `1.mp4`
- `aixia_videos_2026_08_21.zip`
- `gj_dh_res.zip`
- `duix_mobile_test_release_*.apk`

## 本地目录约定

- `*_unpacked/`：对应压缩包的解压目录，可直接找到 `dh_model.p/.b`。
- `Leo`、`Emma` 等人物名包：v2.0.1 人物精调模型。
- `*_optim_m80`：v2.0.0 人物/资源包，网络结构仍属于 165 层新版。

当前 PyTorch 复现见 [`models/MobileNet_Fixed.py`](../models/MobileNet_Fixed.py)。
