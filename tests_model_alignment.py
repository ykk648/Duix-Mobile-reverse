"""Smoke checks for the decrypted DUIX v2.0.1 160px graph."""
from pathlib import Path
import re
import torch

from models.MobileNet_Fixed import MobileNetV2Unet


def parse_weight_bytes(param_path: Path) -> int:
    total = 0
    for line in param_path.read_text().splitlines():
        match = re.search(r"(?:^| )6=(\d+)", line)
        if match:
            total += int(match.group(1))
    return total


def main() -> None:
    model = MobileNetV2Unet().eval()
    face = torch.randn(1, 6, 160, 160)
    audio = torch.randn(1, 256, 20)
    with torch.no_grad():
        out = model(face, audio)
    assert tuple(out.shape) == (1, 3, 160, 160), out.shape
    assert float(out.min()) >= -1.0 and float(out.max()) <= 1.0

    params = sum(p.numel() for p in model.parameters())
    print(f"output={tuple(out.shape)}")
    print(f"pytorch_params={params}")

    model_bin = Path("/tmp/duix_dh_model.bin")
    if model_bin.exists():
        # The released bin stores FP16 weights, hence bytes / 2.
        ncnn_params = model_bin.stat().st_size // 2
        print(f"ncnn_params_from_bin={ncnn_params}")
        assert abs(params - ncnn_params) / params < 0.01


if __name__ == "__main__":
    main()
