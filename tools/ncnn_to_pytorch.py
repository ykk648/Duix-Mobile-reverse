#!/usr/bin/env python3
"""Convert the 165-layer DUIX NCNN model to a PyTorch checkpoint.

The released ``dh_model.b`` stores convolution weights as FP16 and bias/
GroupNorm parameters as FP32.  The converter uses the exact layer order from
``dh_model.p`` and the state-dict order of :class:`MobileNetV2Unet`.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np
import torch

from models.MobileNet_Fixed import MobileNetV2Unet

MAGIC_FP16 = 0x01306B47
CONV_TYPES = {"Convolution", "ConvolutionDepthWise", "Deconvolution"}


def _options(line: str) -> dict[str, str]:
    return {k: v for tok in line.split() if "=" in tok for k, v in [tok.split("=", 1)]}


def _read_f32(raw: bytes, offset: int, count: int) -> tuple[np.ndarray, int]:
    end = offset + count * 4
    if end > len(raw):
        raise ValueError("NCNN bin ended while reading FP32 data")
    return np.frombuffer(raw, dtype="<f4", count=count, offset=offset).copy(), end


def _read_conv(raw: bytes, offset: int, count: int) -> tuple[np.ndarray, int]:
    if offset + 4 > len(raw):
        raise ValueError("NCNN bin ended before a layer magic")
    magic = struct.unpack_from("<I", raw, offset)[0]
    if magic != MAGIC_FP16:
        raise ValueError(f"expected FP16 magic at offset {offset}, got 0x{magic:08x}")
    offset += 4
    end = offset + count * 2
    if end > len(raw):
        raise ValueError("NCNN bin ended while reading FP16 weights")
    value = np.frombuffer(raw, dtype="<f2", count=count, offset=offset).astype(np.float32)
    return value, end


def parse_ncnn(param_path: Path, bin_path: Path) -> list[np.ndarray]:
    """Read trainable tensors in graph order."""
    lines = param_path.read_text().splitlines()
    if not lines or lines[0].strip() != "7767517":
        raise ValueError("not an NCNN param file")
    if lines[1].split()[0] != "165":
        raise ValueError("this converter targets the 165-layer DUIX graph")

    raw = bin_path.read_bytes()
    offset = 0
    tensors: list[np.ndarray] = []
    for line in lines[2:]:
        typ = line.split()[0]
        opts = _options(line)
        if typ in CONV_TYPES:
            count = int(opts["6"])
            weight, offset = _read_conv(raw, offset, count)
            tensors.append(weight)
            if opts.get("5") == "1":
                bias, offset = _read_f32(raw, offset, int(opts["0"]))
                tensors.append(bias)
        elif typ == "GroupNorm":
            channels = int(opts["1"])
            value, offset = _read_f32(raw, offset, channels * 2)
            tensors.extend((value[:channels], value[channels:]))

    if offset != len(raw):
        raise ValueError(f"unconsumed NCNN bytes: offset={offset}, size={len(raw)}")
    return tensors


def convert(param_path: Path, bin_path: Path, output_path: Path) -> None:
    model = MobileNetV2Unet().eval()
    state = model.state_dict()
    tensors = parse_ncnn(param_path, bin_path)
    keys = list(state.keys())
    if len(keys) != len(tensors):
        raise ValueError(f"tensor count mismatch: NCNN={len(tensors)}, torch={len(keys)}")

    converted = {}
    for key, value in zip(keys, tensors):
        expected = state[key]
        if value.size != expected.numel():
            raise ValueError(f"shape/count mismatch for {key}: NCNN={value.size}, torch={tuple(expected.shape)}")
        converted[key] = torch.from_numpy(value.reshape(expected.shape)).to(torch.float32)

    model.load_state_dict(converted, strict=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Keep checkpoints lightweight and training-friendly.  Saving ``model`` in
    # addition to ``state_dict`` duplicates all parameters and nearly doubles
    # the file size (~60 MB instead of ~30 MB for this FP32 model).
    torch.save({
        "state_dict": converted,
        "model_config": {
            "model": "MobileNetV2Unet",
            "input_size": 160,
            "face_shape": [6, 160, 160],
            "audio_shape": [256, 20],
        },
        "source_param": str(param_path),
    }, output_path)
    print(json.dumps({"output": str(output_path), "tensors": len(converted),
                      "parameters": sum(v.numel() for v in converted.values())}, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("param", type=Path)
    ap.add_argument("bin", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    convert(args.param, args.bin, args.output)


if __name__ == "__main__":
    main()
