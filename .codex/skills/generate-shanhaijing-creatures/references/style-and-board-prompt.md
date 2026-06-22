# 风格与 2×2 母板提示词

生成前同时查看 `docs/IMAGE_STYLE_GUIDE.md` 和 `assets/style-reference.png`。以下模板中的四格顺序必须与 `items.json` 一致。

## 批量模式模板

```text
Use case: stylized-concept
Asset type: 《山海异志》网站异兽图鉴 2×2 批量母板
Input image 1: EDIT TARGET. This is the mandatory simplified 4:5 board template. Preserve its portrait 4:5 canvas ratio, one thin plain dark-green outer boundary, one thin plain dark-green central vertical divider, one matching horizontal divider, and four equal portrait 4:5 cells. Paint only inside the four cell interiors. A proportional whole-canvas pixel resample is acceptable; cropping, extending, removing dividers, adding borders, or changing panel geometry is not.
Input image 2: 仅作为画风参考。继承旧米黄宣纸、高密度手绘墨线、墨绿暗金重彩、传统连环画山水、卷云、描金回纹细框、装饰角和民间异兽谱质感；不复制其角色、动作、文字或数字。

Edit Input image 1 in place. The final image must remain portrait 4:5. Each of its four cells must remain portrait 4:5, with boundaries exactly at 50% canvas width and 50% canvas height. Preserve the template's minimal single-line dark-green outer boundary and dark-green center cross. Each cell may contain one restrained antique-gold key-pattern frame inset clearly inside the cell, with small decorative corner ornaments. Gold decoration must not touch or cover the center cross and must not create a gold separator, double border, stacked stripe, or multiple concentric frame. No merged cells, overlaps, irregular collage, outer title, row labels, crop marks, text, numbers, seals, watermark, or UI. Keep every subject and inset frame at least 8% inside its own cell; nothing may cross a midpoint.

Panel order:
TOP LEFT — 【名称 1】：【原文形貌、神能和环境】
TOP RIGHT — 【名称 2】：【原文形貌、神能和环境】
BOTTOM LEFT — 【名称 3】：【原文形貌、神能和环境】
BOTTOM RIGHT — 【名称 4】：【原文形貌、神能和环境】

Unified style for all four panels: 清末彩绘异兽谱、工笔重彩与传统连环画结合；陈旧米黄宣纸，高密度墨线，粗重外轮廓与极细内部纹理；墨绿、暗金、赭石、低饱和朱砂矿物色；完整古典山水、松树、瀑布、卷云；每格允许一层克制的描金回纹细框和小型装饰角。四格必须像同一位画师在同一册书中完成，纸色、线条、饱和度和光线一致。中心十字只能是底板已有的极细墨绿色单线，不得描金，不得增加平行线或多重分割线。

Do not invent standard dragon horns, wings, claws, extra limbs, armor, or magical particles unless the source text explicitly requires them. No anime, game cards, 3D render, photography, neon, gore, modern objects, malformed anatomy, duplicate heads, or cropped bodies.
```

## 变体模式

保持布局和统一风格段不变。四格使用同一异兽和同一原文约束，只改变一个变量：

- 左上：标准三分之二侧面。
- 右上：略低视角，增强神性。
- 左下：环境叙事更强，主体仍占约 70%。
- 右下：最接近古籍博物图的平视全身像。

不要同时改变色盘、年代、媒介或解剖设定。四格用于选稿，不是四种互不相关的风格。

## 生成后目检

依次检查：严格四格、顺序、原文形貌、主体完整、安全边距、无跨格元素、无文字、画风一致。只记录不符合项，不自动重生成整板。完成裁切后交给用户审核；用户明确指出问题时，仅单独调整对应异兽图片。
