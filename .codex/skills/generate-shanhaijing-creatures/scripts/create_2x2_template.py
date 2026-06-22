from pathlib import Path

from PIL import Image, ImageDraw


WIDTH, HEIGHT = 1024, 1280
MID_X, MID_Y = WIDTH // 2, HEIGHT // 2
PAPER = (222, 201, 162)
PINE = (25, 58, 52)
GOLD = (170, 134, 80)


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "assets" / "board-template-4x5.png"
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((3, 3, WIDTH - 4, HEIGHT - 4), outline=PINE, width=6)
    draw.rectangle((11, 11, WIDTH - 12, HEIGHT - 12), outline=GOLD, width=3)
    draw.line((MID_X, 0, MID_X, HEIGHT), fill=PINE, width=12)
    draw.line((0, MID_Y, WIDTH, MID_Y), fill=PINE, width=12)
    draw.line((MID_X - 8, 0, MID_X - 8, HEIGHT), fill=GOLD, width=2)
    draw.line((MID_X + 8, 0, MID_X + 8, HEIGHT), fill=GOLD, width=2)
    draw.line((0, MID_Y - 8, WIDTH, MID_Y - 8), fill=GOLD, width=2)
    draw.line((0, MID_Y + 8, WIDTH, MID_Y + 8), fill=GOLD, width=2)
    for left, top, right, bottom in (
        (18, 18, MID_X - 18, MID_Y - 18),
        (MID_X + 18, 18, WIDTH - 18, MID_Y - 18),
        (18, MID_Y + 18, MID_X - 18, HEIGHT - 18),
        (MID_X + 18, MID_Y + 18, WIDTH - 18, HEIGHT - 18),
    ):
        draw.rectangle((left, top, right, bottom), outline=PINE, width=4)
        draw.rectangle((left + 7, top + 7, right - 7, bottom - 7), outline=GOLD, width=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG", optimize=True)
    print(output)


if __name__ == "__main__":
    main()
