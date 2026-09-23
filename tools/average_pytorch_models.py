#!/usr/bin/env python3
"""Average compatible DUIX PyTorch checkpoints (uniform model soup)."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


def get_state(path: Path) -> dict[str, torch.Tensor]:
    obj = torch.load(path, map_location="cpu", weights_only=False)
    state = obj.get("state_dict", obj) if isinstance(obj, dict) else obj
    if not isinstance(state, dict):
        raise ValueError(f"{path} does not contain a state_dict")
    return {k: v.detach().float().cpu() for k, v in state.items()}


def average(inputs: list[Path], output: Path, trim: bool = False) -> None:
    states = [get_state(p) for p in inputs]
    keys = list(states[0])
    if any(list(s) != keys for s in states[1:]):
        raise ValueError("checkpoint state_dict keys/order differ")
    if any(s[k].shape != states[0][k].shape for s in states for k in keys):
        raise ValueError("checkpoint tensor shapes differ")

    result = {}
    for key in keys:
        stack = torch.stack([s[key] for s in states], dim=0)
        if trim and stack.shape[0] >= 3:
            stack, _ = stack.sort(dim=0)
            stack = stack[1:-1]
        result[key] = stack.mean(dim=0)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": result, "sources": [str(p) for p in inputs],
                "trimmed": trim}, output)
    print(f"saved {output} ({len(result)} tensors, {sum(v.numel() for v in result.values()):,} parameters)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--trimmed", action="store_true",
                    help="drop elementwise min/max before averaging")
    args = ap.parse_args()
    average(args.inputs, args.output, args.trimmed)


if __name__ == "__main__":
    main()
