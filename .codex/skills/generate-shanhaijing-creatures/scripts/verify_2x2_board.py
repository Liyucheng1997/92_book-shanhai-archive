from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageStat


def luminance(image: Image.Image) -> float:
    r, g, b = ImageStat.Stat(image.convert("RGB")).mean
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify true 4:5 geometry and centered seams for a 2x2 board.")
    parser.add_argument("--board", required=True, type=Path)
    args = parser.parse_args()

    image = Image.open(args.board).convert("RGB")
    width, height = image.size
    mid_x, mid_y = round(width / 2), round(height / 2)
    ratio = width / height
    xs = [0, mid_x, width]
    ys = [0, mid_y, height]
    cells = []
    cell_ratios = []
    for row in range(2):
        for col in range(2):
            cell_width = xs[col + 1] - xs[col]
            cell_height = ys[row + 1] - ys[row]
            cell_ratio = cell_width / cell_height
            cells.append([cell_width, cell_height])
            cell_ratios.append(round(cell_ratio, 6))

    seam_half = max(3, round(min(width, height) * 0.004))
    vertical = image.crop((mid_x - seam_half, 0, mid_x + seam_half, height))
    horizontal = image.crop((0, mid_y - seam_half, width, mid_y + seam_half))
    interior = image.crop((round(width * 0.12), round(height * 0.12), round(width * 0.38), round(height * 0.38)))
    interior_luma = luminance(interior)
    vertical_luma = luminance(vertical)
    horizontal_luma = luminance(horizontal)
    vertical_seam = vertical_luma < interior_luma * 0.82
    horizontal_seam = horizontal_luma < interior_luma * 0.82

    ratio_valid = abs(ratio - 0.8) <= 0.01
    cells_valid = all(abs(value - 0.8) <= 0.01 for value in cell_ratios)
    valid = ratio_valid and cells_valid and vertical_seam and horizontal_seam
    result = {
        "valid": valid,
        "board_size": [width, height],
        "board_ratio": round(ratio, 6),
        "midpoint": [mid_x, mid_y],
        "cell_sizes_row_major": cells,
        "cell_ratios": cell_ratios,
        "vertical_seam_detected": vertical_seam,
        "horizontal_seam_detected": horizontal_seam,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
