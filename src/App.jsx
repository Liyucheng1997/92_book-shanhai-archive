import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowUpRight,
  BookOpenText,
  Compass,
  Menu,
  Search,
  X,
} from 'lucide-react'
import { creatures, typeLabels, basisLabels, presentTypes, typeSummary } from './data'

const basisOrder = { text: 0, note: 1, inferred: 2 }
const CATALOGUE_PAGE_SIZE = 6

function ShanHaiMap({ selected, onSelect }) {
  return (
    <div className="map-stage" aria-label="山海经异兽方位示意图">
      <img className="map-bg-image" src="/images/Map.png" alt="" aria-hidden="true" />

      <span className="region-label rl-north">北 · 海外大荒</span>
      <span className="region-label rl-west">西山</span>
      <span className="region-label rl-east">东山</span>
      <span className="region-label rl-center">中山</span>
      <span className="region-label rl-south">南 · 海外大荒</span>

      {creatures.map((c) => {
        const active = c.slug === selected.slug
        return (
          <button
            key={c.slug}
            className={`map-pin ${active ? 'active' : ''}`}
            style={{ left: `${c.mapPos.x * 100}%`, top: `${c.mapPos.y * 100}%` }}
            onClick={() => onSelect(c.slug)}
            aria-label={`${c.name} · ${c.location}`}
            aria-pressed={active}
          >
            <i />
            <span className="map-pin-name">{c.name}</span>
          </button>
        )
      })}

      <div className="map-note">古籍方位示意 · 罗盘相对布局 · 非精确疆域</div>
    </div>
  )
}

export function App() {
  const [selectedId, setSelectedId] = useState(creatures[0]?.slug)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [cataloguePage, setCataloguePage] = useState(0)
  const searchRef = useRef(null)

  const selected = byIdSafe(selectedId)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return creatures.filter((c) => {
      if (typeFilter !== 'all' && c.type !== typeFilter) return false
      if (!q) return true
      return [c.name, c.alias, c.pinyin, c.book, c.location, c.region]
        .join(' ')
        .toLowerCase()
        .includes(q)
    })
  }, [query, typeFilter])

  useEffect(() => setCataloguePage(0), [query, typeFilter])

  const cataloguePageCount = Math.max(1, Math.ceil(filtered.length / CATALOGUE_PAGE_SIZE))
  const safeCataloguePage = Math.min(cataloguePage, cataloguePageCount - 1)
  const pagedCreatures = filtered.slice(
    safeCataloguePage * CATALOGUE_PAGE_SIZE,
    (safeCataloguePage + 1) * CATALOGUE_PAGE_SIZE,
  )

  const selectCreature = (id) => {
    setSelectedId(id)
    setDrawerOpen(false)
  }

  const focusSearch = () => {
    if (window.matchMedia('(max-width: 800px)').matches) setDrawerOpen(true)
    requestAnimationFrame(() => searchRef.current?.focus())
  }

  const scrollToSource = () => {
    document.getElementById('source')?.scrollIntoView({ behavior: 'smooth' })
  }

  const scrollToAtlas = () => {
    document.getElementById('atlas')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="app-shell">
      <div className="grain" />
      <header className="site-header">
        <button className="icon-btn mobile-only" onClick={() => setDrawerOpen(true)} aria-label="打开图鉴目录"><Menu /></button>
        <a className="brand" href="#map" aria-label="山海异志首页"><span className="brand-seal">异志</span><span><b>山海异志</b><small>SHAN HAI ARCHIVE</small></span></a>
        <nav><a className="active" href="#map">山海舆图</a><a href="#atlas">异兽图鉴</a><a href="#source">古籍寻踪</a></nav>
        <button className="search-btn" onClick={focusSearch} aria-label="搜索异兽"><Search size={18} /><span>搜索异兽</span><kbd>{filtered.length}/{creatures.length}</kbd></button>
      </header>

      <main id="top">
        <section className="map-section map-first" id="map">
          <div className="section-heading">
            <div><span className="section-no">壹</span><div><div className="eyebrow">WHERE WAS IT?</div><h1>山海 · 方位舆图</h1></div></div>
            <p>《山海经》的地理体系混合真实见闻、方位叙事与神话想象，无法与今日行政区可靠对应。此图按古籍相对方位作示意布局，点击标记可查看对应记载。</p>
          </div>
          <div className="map-card">
            <div className="map-toolbar">
              <span className="map-hint"><Compass size={15} /> 点击地图标记切换异兽</span>
              <span className="confidence"><i />对应今地可信度：{selected.geoConfidence === 'none' ? '不适用' : '低'}</span>
            </div>
            <ShanHaiMap selected={selected} onSelect={selectCreature} />
            <div className="location-copy">
              <div><span>古籍地点</span><h3>{selected.location}</h3></div>
              <div><span>所属</span><h3>{selected.scroll} · {selected.region}</h3></div>
              <blockquote className="map-quote">“{selected.quote}”</blockquote>
              <button className="map-jump" onClick={scrollToAtlas}>查看{selected.name}图鉴 <ArrowUpRight size={16} /></button>
            </div>
          </div>
        </section>

        <section className="atlas-section" id="atlas" aria-labelledby="atlas-title">
          <div className="atlas-heading section-heading">
            <div><span className="section-no">贰</span><div><div className="eyebrow">CREATURE ARCHIVE</div><h2 id="atlas-title">异兽 · 图鉴目录</h2></div></div>
            <p>依十八卷篇目与卷内次序辑录。通过左侧分页目录筛选异物，图版、原文和考据会同步切换。</p>
          </div>

          <div className="hero">
          <aside className={`catalogue ${drawerOpen ? 'open' : ''}`}>
            <button className="close-drawer mobile-only" onClick={() => setDrawerOpen(false)} aria-label="关闭目录"><X /></button>
            <div className="eyebrow"><BookOpenText size={15} /> 异兽目录</div>
            <h2>已录 {creatures.length} 种</h2>
            <div className="chapter-rule"><span>{typeSummary()}</span></div>

            <div className="search-box">
              <Search size={15} />
              <input
                ref={searchRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="搜索名称、山名或篇目"
                aria-label="搜索异兽"
              />
              {query && <button className="clear-search" onClick={() => setQuery('')} aria-label="清除搜索"><X size={14} /></button>}
            </div>

            <div className="type-filter" role="group" aria-label="按类别筛选">
              <button className={typeFilter === 'all' ? 'active' : ''} onClick={() => setTypeFilter('all')}>全部</button>
              {presentTypes.map((t) => (
                <button key={t} className={typeFilter === t ? 'active' : ''} onClick={() => setTypeFilter(t)}>{typeLabels[t]}</button>
              ))}
            </div>

            <div className="creature-list">
              {pagedCreatures.map((item) => (
                <button key={item.slug} className={item.slug === selected.slug ? 'active' : ''} onClick={() => selectCreature(item.slug)} aria-pressed={item.slug === selected.slug}>
                  <span className="list-index">{typeLabels[item.type]}</span>
                  <span><b>{item.name}</b><small>{item.book} · {item.location}</small></span>
                  {item.slug === selected.slug && <i />}
                </button>
              ))}
              {filtered.length === 0 && <p className="empty-hint">未找到匹配的异兽</p>}
            </div>
            <div className="catalogue-pagination" aria-label="异兽目录分页">
              <button
                onClick={() => setCataloguePage((page) => Math.max(0, page - 1))}
                disabled={safeCataloguePage === 0}
                aria-label="上一页"
              >上一页</button>
              <span>第 {safeCataloguePage + 1} / {cataloguePageCount} 页</span>
              <button
                onClick={() => setCataloguePage((page) => Math.min(cataloguePageCount - 1, page + 1))}
                disabled={safeCataloguePage >= cataloguePageCount - 1}
                aria-label="下一页"
              >下一页</button>
            </div>
            <div className="coming-soon">据《山海经》十八卷次第辑录 · 持续增补</div>
          </aside>

          <div className="hero-art">
            <div className="vertical-title" aria-hidden="true">{selected.location}</div>
            <div className="sun-moon"><BookOpenText /><span /><Compass /></div>
            <div className={`illustration-card ${selected.imageClass || ''}`}>
              <i className="corner corner-tl" /><i className="corner corner-tr" /><i className="corner corner-bl" /><i className="corner corner-br" />
              <img key={selected.slug} src={selected.image} alt={selected.imageAlt} />
              <div className="plate-title"><span>{selected.plate}</span><div><b>{selected.name}</b><small>{selected.imageTag}</small></div></div>
            </div>
            <span className="art-caption">山海异兽绘卷 · {selected.book}</span>
          </div>

          <article className="creature-copy" key={selected.slug}>
            <div className="eyebrow"><Compass size={15} /> {selected.scroll} · {selected.book} · {typeLabels[selected.type]}类</div>
            <div className="name-row"><h1>{selected.name}</h1><span>{selected.alias}</span></div>
            <p className="pinyin">{selected.pinyin}</p>
            {selected.tags?.length > 0 && (
              <div className="tag-row">{selected.tags.map((t) => <span key={t}>{t}</span>)}</div>
            )}
            <blockquote>“{selected.quote}”<cite>——《山海经 · {selected.book}》</cite></blockquote>
            <p className="summary">{selected.summary}</p>
            <dl className="facts">
              {selected.facts.map(({ label, value, basis }) => (
                <div key={label}>
                  <dt>{label}</dt>
                  <dd>{value}<em className={`basis basis-${basis}`}>{basisLabels[basis] ?? basis}</em></dd>
                </div>
              ))}
            </dl>
            <button className="read-more" onClick={scrollToSource}>查阅完整考据 <ArrowUpRight size={17} /></button>
          </article>
          </div>
        </section>

        <section className="source-section" id="source">
          <div className="source-mark">{selected.mark}</div>
          <div className="source-body">
            <div className="eyebrow">TEXTUAL RECORD</div>
            <h2>古籍寻踪 · {selected.name}</h2>
            <p>{selected.sourceNote}</p>
            {selected.references?.length > 0 && (
              <ul className="references">
                {selected.references.map((ref, i) => (
                  <li key={i}><span>《{ref.book}》</span>{ref.text}</li>
                ))}
              </ul>
            )}
            <a href="#top">返回图鉴 <ArrowUpRight size={17} /></a>
          </div>
        </section>
      </main>
      <footer><span>山海异志 · 数字图鉴计划</span><span>据古籍辑录，供阅读与研究参考</span></footer>
    </div>
  )
}

function byIdSafe(id) {
  return creatures.find((c) => c.slug === id) ?? creatures[0]
}
