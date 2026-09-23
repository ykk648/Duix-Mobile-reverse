# NCNN → PyTorch 权重转换

`tools/ncnn_to_pytorch.py` 针对 165 层 DUIX graph，将解密后的 `dh_model.p`
和 `dh_model.b` 转成 PyTorch checkpoint，便于进行结构验证和后续研究。

## 转换 Leo

```bash
python3 tools/decrypt_model.py download/Leo_unpacked/Leo/dh_model.p /tmp/Leo.param
python3 tools/decrypt_model.py download/Leo_unpacked/Leo/dh_model.b /tmp/Leo.bin
PYTHONPATH=. python3 tools/ncnn_to_pytorch.py \
  /tmp/Leo.param /tmp/Leo.bin checkpoints/Leo.pt
```

输出 checkpoint 包含：

```python
obj = torch.load("checkpoints/Leo.pt", map_location="cpu")
state_dict = obj["state_dict"]
```

当前 Leo 转换结果为 187 个张量、7,506,139 个参数，与 `.param` 推导的参数数目一致。
NCNN 卷积权重以 FP16 保存，转换后统一保存为 FP32，适合继续训练。

## 多模型参数平均

先把多个同结构人物包分别转换成 `.pt`，再平均：

```bash
PYTHONPATH=. python3 tools/average_pytorch_models.py \
  checkpoints/Leo.pt checkpoints/Emma.pt checkpoints/Kai.pt \
  checkpoints/Lily.pt checkpoints/Oliver.pt checkpoints/Sofia.pt \
  --output checkpoints/duix_mean.pt
```

也可以使用截尾均值，减少某个精调人物偏移过大的影响：

```bash
PYTHONPATH=. python3 tools/average_pytorch_models.py \
  checkpoints/*.pt --trimmed --output checkpoints/duix_trimmed_mean.pt
```

只平均 `docs/release_model_catalog.md` 中列出的 165 层模型，不要混入
`airuike_20240409` 或 `bendi3_20240518`。
