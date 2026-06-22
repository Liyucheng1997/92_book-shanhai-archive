// 自动收集 src/data/creatures/ 下的所有条目。
// 新增异兽 = 在该目录放一个 <slug>.json，无需改动本文件或 App.jsx。
// 排序与分类规则见 docs/DATA_SCHEMA.md。

const modules = import.meta.glob('./creatures/*.json', { eager: true })

const all = Object.values(modules).map((mod) => mod.default ?? mod)

// 通行十八卷本顺序（volume 字段即此序号）。
export const volumeOrder = [
  '南山经', '西山经', '北山经', '东山经', '中山经',
  '海外南经', '海外西经', '海外北经', '海外东经',
  '海内南经', '海内西经', '海内北经', '海内东经',
  '大荒东经', '大荒南经', '大荒西经', '大荒北经', '海内经',
]

// 先按卷序，再按卷内出场顺序 seq，最后按 slug 兜底。
export const creatures = all.slice().sort(
  (a, b) => (a.volume - b.volume) || (a.seq - b.seq) || a.slug.localeCompare(b.slug)
)

export const typeLabels = {
  deity: '神',
  beast: '兽',
  bird: '禽',
  fish: '鳞',
  serpent: '蛇虫',
  figure: '异人',
}

export const basisLabels = {
  text: '原文',
  inferred: '推定',
  note: '注',
}

export const byId = Object.fromEntries(creatures.map((c) => [c.slug, c]))

// 当前数据里实际出现过的分类，用于筛选条（保持 typeLabels 的顺序）。
export const presentTypes = Object.keys(typeLabels).filter(
  (t) => creatures.some((c) => c.type === t)
)

// 目录小标题用：「神怪一 · 兽类四」之类的自动统计。
export function typeSummary() {
  const counts = {}
  for (const c of creatures) counts[c.type] = (counts[c.type] || 0) + 1
  return presentTypes.map((t) => `${typeLabels[t]} ${counts[t]}`).join(' · ')
}
