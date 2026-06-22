---
name: generate-shanhaijing-creatures
description: Generate project-consistent Shanhaijing creature artwork economically through one strict 2x2 Image Gen board, then isolate the new master, crop exact quadrants, run each raw crop directly through Real-ESRGAN x4, and publish optimized website assets. Use when adding or regenerating creature illustrations for this 山海经图鉴 project, when the user says 批量生图、2x2 生图、异兽生图、生成四只异兽、生成四个方案、裁切高清化、替换图鉴图片, or asks to reduce Image Gen usage for project artwork.
---

# 山海异兽 2×2 生图流水线

用一次 Image Gen 生成四个可交付画面。默认批量模式是一板四只异兽；需要选稿时使用变体模式，同一异兽一板四稿。

## 固定路径

从 skill 目录向上三级定位项目根目录。使用：

- 风格规范：`docs/IMAGE_STYLE_GUIDE.md`
- 风格参考：`.codex/skills/generate-shanhaijing-creatures/assets/style-reference.png`
- 标准比例参考：`public/images/creature_zhulong_v01.png`
- 强制母板模板：`.codex/skills/generate-shanhaijing-creatures/assets/board-template-4x5.png`
- 批次记录：`artifacts/imagegen/<batch-id>/`
- 网站图片：`public/images/creatures/`
- 处理脚本：`scripts/finalize_2x2_board.py`
- Real-ESRGAN：`F:\Real-ESRGAN\realesrgan-ncnn-vulkan-20210901-windows\realesrgan-ncnn-vulkan.exe`

需要写 Image Gen 提示词时读取 [references/style-and-board-prompt.md](references/style-and-board-prompt.md)。

## 工作流

### 1. 建立批次

创建唯一目录：

```text
artifacts/imagegen/<YYYYMMDD-HHMMSS>-<short-name>/
├── items.json
├── prompt.md
├── masters/board.png
└── manifest.json
```

不要复用其他会话的临时目录。`items.json` 必须恰好包含四项，并按左上、右上、左下、右下排序：

```json
[
  {"slug":"zhulong","name":"烛阴","version":"v01"},
  {"slug":"jiuweihu","name":"九尾狐","version":"v01"},
  {"slug":"qiongqi","name":"穷奇","version":"v01"},
  {"slug":"kui","name":"夔","version":"v01"}
]
```

变体模式也保留四项，但使用不同版本号，例如 `v01a` 至 `v01d`。

### 2. 生成严格 2×2 母板

使用内置 `image_gen`，每块母板只调用一次。必须把 `board-template-4x5.png` 作为编辑底板，把风格图片标记为风格参考。要求模型保持底板的 4:5 画布、外框、中线和四格比例，只在四格内部绘画。允许 Image Gen 对整张底板做等比例像素重采样，但不得改变 4:5 比例或中线位置。不得只靠文字描述或普通比例参考生成空白母板。首次生成完成后立即停止生图，不得由执行者自行重生成整板。

生成前递归记录 `C:\Users\liyuc\.codex\generated_images\` 的已有 PNG 及时间。生成后立即识别本次唯一新增文件，复制到当前批次的 `masters/board.png`。不要在多个生成任务完成后通过“最新图片”猜测文件。

母板必须满足：

- 整张画布必须与烛龙主图完全相同，为竖版 4:5；严格 2 列 × 2 行。生成提示词中写明 `exact portrait 4:5 canvas, same aspect ratio as the Zhulong reference, not 2:3 and not 5:8`。
- 四个面板尺寸完全相等，分界线恰好位于宽、高的 1/2。
- 使用细而均匀的旧纸色分隔线；不合并、不重叠、不做自由拼贴。
- 每个面板自身也是 4:5，主体和边框完整。
- 所有重要内容距离面板边缘至少 8%；不得跨越中线。
- 四格不生成文字、数字、印章、标签、水印或 UI。
- 批量模式严格按 `items.json` 顺序放置四只异兽。
- 生成后先读取像素尺寸。母板宽高比必须为 4:5（允许编码造成的极小误差），每个半幅裁片也必须为 4:5。任何一项不符合时立即停止；禁止裁切、高清化、补边、拉伸或更新网站。
- 在裁切前运行 `scripts/verify_2x2_board.py --board <母板>`。只有 `valid: true` 才能继续。
- 首次母板即为本批审核稿。发现局部形貌、计数、肢体或构图问题时，在批次记录中标记问题，但仍裁切其余可审核图片。
- 不得因为一格有问题而重新生成整张 2×2 母板。用户审核后，只对明确指出的问题图单独编辑或生成；除非用户明确要求，不影响同批其他三图。

生成结果必须复制进项目后才能继续，不能让网站依赖 Codex 共享生成目录。

### 3. 裁切和高清化

运行：

```powershell
python ".codex\skills\generate-shanhaijing-creatures\scripts\finalize_2x2_board.py" `
  --board "artifacts\imagegen\<batch-id>\masters\board.png" `
  --items "artifacts\imagegen\<batch-id>\items.json" `
  --run-root "artifacts\imagegen\<batch-id>"
```

脚本必须执行以下固定顺序：

1. 以精确半幅坐标裁切四格，不做视觉猜测。
2. 把原始裁片直接送入 Real-ESRGAN `realesrgan-x4plus -s 4`。
3. 将 x4 输出固定缩至 1600×2000；不得使用其他成品尺寸。
4. 输出 WebP（质量 88）到 `public/images/creatures/creature_<slug>_<version>.webp`。
5. 写入裁切坐标、哈希、尺寸及工具参数到批次 `manifest.json`。

禁止在 Real-ESRGAN 之前使用 Pillow/Lanczos 放大。临时 raw/x4 文件只能位于隔离的 `C:\tmp\shanhaijing_imagegen_<batch-id>`，不能进入网站资产目录。

默认禁止覆盖已有图片。只有用户明确要求替换时传 `--overwrite`。脚本不提供自定义宽高参数，所有正式成品统一为 1600×2000。

### 4. 接入网页

将条目图片路径指向对应 WebP。保留语义化 `alt`。构建并验证：

```powershell
npm run build
```

检查图片成功加载、无控制台错误、桌面与移动端无横向溢出。除非用户要求，不保留 PNG 网站副本。

## 质量门槛

完成前确认：

- 只有一张 2×2 AI 母板对应本批四张成品。
- 母板为真正 4:5 且严格半幅分割；每个原始半幅裁片也是 4:5，不依赖后期装裱或补边。
- 对照原文记录每只异兽的符合项与待审核项；待审核项不得触发自动重生成。
- 四格画风、纸色、墨线密度、边框和色盘一致。
- 每张成品为 1600×2000 WebP。
- 原始裁片直接进入 Real-ESRGAN。
- `manifest.json` 存在并记录 SHA-256。
- 网站构建通过。

若 Real-ESRGAN 缺失或失败，停止并报告，不得静默改用普通插值冒充高清化。若生成画面存在问题，等待用户决定是否单独调整，不得擅自追加 Image Gen 调用。

## 响应格式

简短报告批次目录、四张网站图片和构建结果。若发生重生成或质检失败，明确说明。
