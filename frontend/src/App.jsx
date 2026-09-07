import { useEffect, useMemo, useState } from 'react'
import './App.css'
import HomePage from './HomePage'
import AdvancedChartWidget from './widgets/AdvancedChartWidget'
import FundamentalDataWidget from './widgets/FundamentalDataWidget'
import SymbolInfoWidget from './widgets/SymbolInfoWidget'

const WATCHLIST_SIZE = 20

const EXCHANGE_BY_SYMBOL = {
  AAPL: 'NASDAQ', MSFT: 'NASDAQ', GOOGL: 'NASDAQ', AMZN: 'NASDAQ', NVDA: 'NASDAQ',
  META: 'NASDAQ', TSLA: 'NASDAQ', AMD: 'NASDAQ', NFLX: 'NASDAQ', COIN: 'NASDAQ', INTC: 'NASDAQ',
  DIS: 'NYSE', JPM: 'NYSE', V: 'NYSE', JNJ: 'NYSE', PFE: 'NYSE', WMT: 'NYSE', KO: 'NYSE', XOM: 'NYSE', BA: 'NYSE',
}

function qualifiedSymbol(symbol) {
  const exchange = EXCHANGE_BY_SYMBOL[symbol]
  return exchange ? `${exchange}:${symbol}` : symbol
}

const MOVE_META = {
  top_gainer: { title: 'Top Gainers', tone: 'gain', glyph: '▲' },
  top_loser: { title: 'Top Losers', tone: 'loss', glyph: '▼' },
  volume_spike: { title: 'Volume Spikes', tone: 'spike', glyph: '⚡' },
  relative_performance: { title: 'Relative Performance', tone: 'relative', glyph: '★' },
}

function groupByType(moves) {
  const groups = { top_gainer: [], top_loser: [], volume_spike: [], relative_performance: [] }
  for (const move of moves) {
    if (groups[move.move_type]) {
      groups[move.move_type].push(move)
    }
  }
  return groups
}
function magnitude(moveType, value) {
  const size = Math.abs(value)
  const bounds = moveType === 'volume_spike' ? [3, 5] : [2, 5]
  if (size >= bounds[1]) return 'high'
  if (size >= bounds[0]) return 'mid'
  return 'low'
}

function WhyButton({ date, symbol }) {
  const [state, setState] = useState('idle') 
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  const handleClick = () => {
    if (state === 'loading') return
    setState('loading')

    fetch(`/api/explain/${date}/${symbol}`)
      .then(async (res) => {
        const body = await res.json()
        if (!res.ok) {
          throw new Error(body.detail || 'Something went wrong.')
        }
        setResult(body)
        setState('done')
      })
      .catch((err) => {
        setErrorMsg(err.message)
        setState('error')
      })
  }

  if (state === 'idle') {
    return (
      <button type="button" className="why-button" onClick={handleClick}>
        Why?
      </button>
    )
  }

  if (state === 'loading') {
    return <span className="why-loading">Thinking...</span>
  }

  if (state === 'error') {
    return <p className="why-error">{errorMsg}</p>
  }

  return (
    <div className="why-result">
      <p>{result.explanation}</p>
      <p className="why-disclaimer">{result.disclaimer}</p>
    </div>
  )
}


function ChartButton({ symbol }) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button type="button" className="chart-button" onClick={() => setOpen((v) => !v)}>
        {open ? 'Hide chart' : 'Chart'}
      </button>
      {open && (
        <div className="tv-chart-wrap">
          <AdvancedChartWidget symbol={symbol} />
        </div>
      )}
    </>
  )
}


function DetailsButton({ symbol }) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button type="button" className="chart-button" onClick={() => setOpen((v) => !v)}>
        {open ? 'Hide details' : 'Details'}
      </button>
      {open && (
        <div className="tv-details-wrap">
          <SymbolInfoWidget symbol={symbol} />
          <div style={{ width: '100%', minWidth: 0 }}>
            <tv-technical-analysis symbol={qualifiedSymbol(symbol)} theme="dark"></tv-technical-analysis>
          </div>
          <div style={{ width: '100%', minWidth: 0 }}>
            <tv-company-profile symbol={symbol} theme="dark"></tv-company-profile>
          </div>
          <FundamentalDataWidget symbol={symbol} />
        </div>
      )}
    </>
  )
}

function MoveCard({ moveType, moves, formatValue, date }) {
  const meta = MOVE_META[moveType]

  return (
    <div className={`move-card tone-${meta.tone}`}>
      <div className="move-card-header">{meta.title}</div>
      {moves.length === 0 ? (
        <p className="move-card-empty">Nothing matches the current filters.</p>
      ) : (
        <ul>
          {moves.map((move) => (
            <li key={move.symbol} className={`mag-${magnitude(moveType, move.value)}`}>
              <div className="move-row">
                <span className="glyph">{meta.glyph}</span>
                <span className="symbol">{move.symbol}</span>
                <span className="name">{move.name}</span>
                <span className="value">{formatValue(move.value)}</span>
              </div>
              <div className="row-actions">
                <WhyButton date={date} symbol={move.symbol} />
                <ChartButton symbol={move.symbol} />
                <DetailsButton symbol={move.symbol} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function App() {
  const [dates, setDates] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [moves, setMoves] = useState(null)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [sector, setSector] = useState('')
  const [page, setPage] = useState('home') // home dashboard

  useEffect(() => {
    fetch('/api/snapshots')
      .then((res) => res.json())
      .then(setDates)
      .catch(() => setError('Could not load snapshot dates.'))
  }, [])

  useEffect(() => {
    const url = selectedDate ? `/api/snapshots/${selectedDate}` : '/api/snapshots/latest'
    setError(null)
    setMoves(null)
    setSearch('')
    setSector('')

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error('no data for that date')
        }
        return res.json()
      })
      .then((data) => setMoves(data))
      .catch(() => setError('No snapshot yet. run fetch_prices and compute_moves first.'))
  }, [selectedDate])

  const sectors = useMemo(() => {
    if (!moves) return []
    return [...new Set(moves.moves.map((m) => m.sector))].sort()
  }, [moves])

  const filtered = useMemo(() => {
    if (!moves) return null
    const q = search.trim().toLowerCase()
    return moves.moves.filter((m) => {
      const matchesSearch = !q || m.symbol.toLowerCase().includes(q) || m.name.toLowerCase().includes(q)
      const matchesSector = !sector || m.sector === sector
      return matchesSearch && matchesSector
    })
  }, [moves, search, sector])

  const grouped = filtered ? groupByType(filtered) : null
  const hasActiveFilters = search !== '' || sector !== ''

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">Stock Snap</div>
        <nav className="sidebar-nav">
          <button
            type="button"
            className={page === 'home' ? 'nav-link nav-link-active' : 'nav-link'}
            onClick={() => setPage('home')}
          >
            Home
          </button>
          <button
            type="button"
            className={page === 'dashboard' ? 'nav-link nav-link-active' : 'nav-link'}
            onClick={() => setPage('dashboard')}
          >
            Dashboard
          </button>
        </nav>
        <div className="sidebar-block">
          <div className="sidebar-row">
            <span className="sidebar-label">Data source</span>
            <span>Alpha Vantage</span>
          </div>
          <div className="sidebar-row">
            <span className="sidebar-label">Schedule</span>
            <span>Daily</span>
          </div>
          <div className="sidebar-row">
            <span className="sidebar-label">Watchlist</span>
            <span>Tickers</span>
          </div>
        </div>
      </aside>

      <main className="content content-wide">
        {page === 'home' ? (
          <HomePage />
        ) : (
          <>
            <div className="topbar">
              <div>
                <h1>Today's Moves</h1>
                <p className="subtitle">Gainers, losers, and unusual volume across the watchlist</p>
              </div>
              <div className="date-picker">
                <label htmlFor="date-select">Date</label>
                <select
                  id="date-select"
                  value={selectedDate ?? ''}
                  onChange={(e) => setSelectedDate(e.target.value || null)}
                >
                  <option value="">Latest</option>
                  {dates.map((date) => (
                    <option key={date} value={date}>
                      {date}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {error && <p className="error">{error}</p>}

            {moves && (
              <>
                <div className="stat-row">
                  <div className="stat-tile">
                    <span className="stat-value">{filtered.length}</span>
                    <span className="stat-label">
                      {hasActiveFilters ? `Movers Matching (of ${moves.moves.length})` : 'Movers Flagged'}
                    </span>
                  </div>
                  <div className="stat-tile">
                    <span className="stat-value">{WATCHLIST_SIZE}</span>
                    <span className="stat-label">Tickers Tracked</span>
                  </div>
                  <div className="stat-tile">
                    <span className="stat-value">{moves.date}</span>
                    <span className="stat-label">Snapshot Date</span>
                  </div>
                </div>

                <div className="filter-row">
                  <input
                    type="text"
                    className="search-input"
                    placeholder="Search ticker or company..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  <select value={sector} onChange={(e) => setSector(e.target.value)}>
                    <option value="">All sectors</option>
                    {sectors.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                  {hasActiveFilters && (
                    <button
                      type="button"
                      className="clear-filters"
                      onClick={() => {
                        setSearch('')
                        setSector('')
                      }}
                    >
                      Clear filters
                    </button>
                  )}
                </div>

                <div className="move-grid">
                  <MoveCard
                    moveType="top_gainer"
                    moves={grouped.top_gainer}
                    formatValue={(v) => `+${v.toFixed(2)}%`}
                    date={moves.date}
                  />
                  <MoveCard
                    moveType="top_loser"
                    moves={grouped.top_loser}
                    formatValue={(v) => `${v.toFixed(2)}%`}
                    date={moves.date}
                  />
                  <MoveCard
                    moveType="volume_spike"
                    moves={grouped.volume_spike}
                    formatValue={(v) => `${v.toFixed(1)}x avg`}
                    date={moves.date}
                  />
                  <MoveCard
                    moveType="relative_performance"
                    moves={grouped.relative_performance}
                    formatValue={(v) => `${v > 0 ? '+' : ''}${v.toFixed(2)}% vs sector`}
                    date={moves.date}
                  />
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
