# 山海异志

《山海经》异兽数字图鉴。工笔重彩风格的 AI 异兽图 + 可考据的古籍条目 + 方位示意舆图。

当前版本：**v1.1.0**

## 本地运行

```bash
npm install
npm run dev
```

## 构建

```bash
npm run build
```

## 目录结构

```
src/
  data/
    creatures/        每只异兽一个 <slug>.json（新增条目只动这里）
    index.js          自动收集、按卷序排序、导出辅助函数
  App.jsx             界面（不写死数据）
  styles.css
docs/
  DATA_SCHEMA.md      数据字段 / 分类 / 排序契约（Codex 必读）
  CREATURE_CHECKLIST.md  按卷序排好的生成队列，每批 4 只
  IMAGE_STYLE_GUIDE.md   统一图像风格规范
.codex/skills/        2×2 母板生图流水线 skill
artifacts/imagegen/   每批生图的母板与记录
public/images/        网站图片资产
```

## 新增一只异兽

1. 用 `.codex` 里的 2×2 流水线生成图片，得到 `public/images/creatures/creature_<slug>_v03.webp`。
2. 在 `src/data/creatures/` 新建 `<slug>.json`，字段严格按 [docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md)。
3. 无需改动 `App.jsx` 或 `index.js`，前端会自动收录、排序、上图、上地图。

图像生成规范见 [docs/IMAGE_STYLE_GUIDE.md](docs/IMAGE_STYLE_GUIDE.md)。
