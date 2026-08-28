import { useEffect, useState } from 'react'
import './App.css'

const MOVE_LABELS = {
  top_gainer: 'Top Gainers',
  top_loser: 'Top Losers',
  volume_spike: 'Volume Spikes',
}

function groupByType(moves) {
  const groups = { top_gainer: [], top_loser: [], volume_spike: [] }
  for (const move of moves) {
    if (groups[move.move_type]) {
      groups[move.move_type].push(move)
    }
  }
  return groups
}

function MoveList({ title, moves, formatValue }) {
  if (moves.length === 0) {
    return null
  }

  return (
    <div className="move-list">
      <h2>{title}</h2>
      <ul>
        {moves.map((move) => (
          <li key={move.symbol}>
            <span className="symbol">{move.symbol}</span>
            <span className="name">{move.name}</span>
            <span className="value">{formatValue(move.value)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function App() {
  const [dates, setDates] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [moves, setMoves] = useState(null)
  const [error, setError] = useState(null)

  
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

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error('no data for that date')
        }
        return res.json()
      })
      .then((data) => setMoves(data))
      .catch(() => setError('No snapshot data yet. run fetch_prices and compute_moves first.'))
  }, [selectedDate])

  const grouped = moves ? groupByType(moves.moves) : null

  return (
    <div className="app">
      <header>
        <h1>Stock Snap</h1>
        <p className="subtitle">Daily snapshot of interesting stock moves</p>
      </header>

      <div className="date-picker">
        <label htmlFor="date-select">Date:</label>
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

      {error && <p className="error">{error}</p>}

      {moves && (
        <>
          <p className="snapshot-date">Showing: {moves.date}</p>
          <div className="move-grid">
            <MoveList
              title={MOVE_LABELS.top_gainer}
              moves={grouped.top_gainer}
              formatValue={(v) => `+${v.toFixed(2)}%`}
            />
            <MoveList
              title={MOVE_LABELS.top_loser}
              moves={grouped.top_loser}
              formatValue={(v) => `${v.toFixed(2)}%`}
            />
            <MoveList
              title={MOVE_LABELS.volume_spike}
              moves={grouped.volume_spike}
              formatValue={(v) => `${v.toFixed(1)}x avg`}
            />
          </div>
        </>
      )}
    </div>
  )
}

export default App
