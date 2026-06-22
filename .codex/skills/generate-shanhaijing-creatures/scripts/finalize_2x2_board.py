from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PIL import Image


DEFAULT_REALESRGAN = Path(
    r"F:\Real-ESRGAN\realesrgan-ncnn-vulkan-20210901-windows\realesrgan-ncnn-vulkan.exe"
)
FINAL_SIZE = (1600, 2000)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_points(size: int) -> list[int]:
    return [0, round(size / 2), size]


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError(f"Invalid slug: {value!r}")
    return slug


def load_items(path: Path) -> list[dict]:
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list) or len(items) != 4:
        raise ValueError("items.json must contain exactly four entries")
    result = []
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not item.get("slug") or not item.get("name"):
            raise ValueError(f"Item {index + 1} requires slug and name")
        slug = safe_slug(str(item["slug"]))
        version = str(item.get("version", "v01"))
        if not re.fullmatch(r"v[0-9]+[a-z]?", version):
            raise ValueError(f"Invalid version for {slug}: {version}")
        key = (slug, version)
        if key in seen:
            raise ValueError(f"Duplicate output key: {slug} {version}")
        seen.add(key)
        result.append({**item, "slug": slug, "version": version})
    return result


def prepare_tmp(path: Path) -> Path:
    resolved = path.resolve()
    expected_root = Path(r"C:\tmp").resolve()
    if expected_root not in resolved.parents:
        raise ValueError(f"Temporary folder must stay under {expected_root}: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    (resolved / "raw").mkdir(parents=True)
    (resolved / "x4").mkdir(parents=True)
    return resolved


def crop_quadrant(board: Image.Image, index: int) -> tuple[Image.Image, dict]:
    row, col = divmod(index, 2)
    xs = split_points(board.width)
    ys = split_points(board.height)
    box = (xs[col], ys[row], xs[col + 1], ys[row + 1])
    return board.crop(box), {
        "row": row + 1,
        "col": col + 1,
        "coords": list(box),
        "source_size": [board.width, board.height],
    }


def run_realesrgan(executable: Path, source: Path, destination: Path) -> None:
    subprocess.run(
        [
            str(executable),
            "-i",
            str(source),
            "-o",
            str(destination),
            "-n",
            "realesrgan-x4plus",
            "-s",
            "4",
            "-f",
            "png",
        ],
        check=True,
    )


def save_webp(source: Path, destination: Path, size: tuple[int, int]) -> dict:
    image = Image.open(source).convert("RGB")
    target_ratio = size[0] / size[1]
    source_ratio = image.width / image.height
    if abs(source_ratio - target_ratio) > 0.01:
        raise ValueError(f"Cell is not true 4:5: {image.width}x{image.height} ({source_ratio:.6f})")
    final = image.resize(size, Image.Resampling.LANCZOS)
    final.save(destination, "WEBP", quality=88, method=6)
    return {"normalization": "none_true_4x5_source", "source_ratio": round(source_ratio, 6)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Crop a strict 2x2 Shanhaijing board, upscale raw cells with Real-ESRGAN, and publish WebP assets."
    )
    parser.add_argument("--board", required=True, type=Path)
    parser.add_argument("--items", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--tmp", type=Path)
    parser.add_argument("--realesrgan", type=Path, default=DEFAULT_REALESRGAN)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--skip-upscale",
        action="store_true",
        help="Testing only: skip Real-ESRGAN and use raw crops as enhancement inputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_project_root = Path(__file__).resolve().parents[4]
    project_root = (args.project_root or script_project_root).resolve()
    run_root = args.run_root.resolve()
    output_dir = (args.output_dir or project_root / "public" / "images" / "creatures").resolve()
    batch_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_root.name)
    tmp = args.tmp or Path(r"C:\tmp") / f"shanhaijing_imagegen_{batch_id}"

    for required in (args.board, args.items):
        if not required.exists():
            raise FileNotFoundError(required)
    if not args.skip_upscale and not args.realesrgan.exists():
        raise FileNotFoundError(args.realesrgan)
    items = load_items(args.items)
    board = Image.open(args.board).convert("RGB")
    board_ratio = board.width / board.height
    if abs(board_ratio - 0.8) > 0.01:
        raise ValueError(f"Board is not true 4:5: {board.width}x{board.height} ({board_ratio:.6f})")

    destinations = [
        output_dir / f"creature_{item['slug']}_{item['version']}.webp" for item in items
    ]
    conflicts = [path for path in destinations if path.exists()]
    if conflicts and not args.overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing assets: " + ", ".join(str(path) for path in conflicts)
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    tmp = prepare_tmp(tmp)
    records = []

    for index, (item, destination) in enumerate(zip(items, destinations)):
        crop, crop_info = crop_quadrant(board, index)
        stem = f"{index + 1:02d}_{item['slug']}_{item['version']}"
        raw_path = tmp / "raw" / f"{stem}.png"
        x4_path = tmp / "x4" / f"{stem}.png"
        crop.save(raw_path, "PNG", optimize=True)

        if args.skip_upscale:
            x4_path = raw_path
            operation = "test_only_raw_crop_then_downsize"
        else:
            run_realesrgan(args.realesrgan, raw_path, x4_path)
            operation = "raw_crop_direct_to_realesrgan_x4_then_downsize_to_webp"

        normalization_info = save_webp(x4_path, destination, FINAL_SIZE)
        records.append(
            {
                "name": item["name"],
                "slug": item["slug"],
                "version": item["version"],
                **crop_info,
                "raw_crop_tmp": str(raw_path),
                "realesrgan_x4_tmp": str(x4_path),
                "final_path": str(destination),
                "final_size": list(Image.open(destination).size),
                "sha256": sha256(destination),
                "operation": operation,
                **normalization_info,
            }
        )

    manifest = {
        "workflow": "Shanhaijing 2x2 Image Pipeline v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "run_root": str(run_root),
        "master_board": str(args.board.resolve()),
        "master_board_sha256": sha256(args.board),
        "items_file": str(args.items.resolve()),
        "tmp_folder": str(tmp),
        "crop_strategy": "exact_halves_row_major",
        "master_board_ratio": round(board_ratio, 6),
        "realesrgan": {
            "enabled": not args.skip_upscale,
            "executable": str(args.realesrgan),
            "model": "realesrgan-x4plus",
            "scale": 4,
            "rule": "raw crops go directly to Real-ESRGAN; no pre-upscaling",
        },
        "web_output": {"format": "webp", "quality": 88, "size": list(FINAL_SIZE)},
        "outputs": records,
    }
    manifest_path = run_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "outputs": [str(p) for p in destinations]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
