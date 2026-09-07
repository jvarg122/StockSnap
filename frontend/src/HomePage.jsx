import EconomicCalendarWidget from './widgets/EconomicCalendarWidget'
import StockHeatmapWidget from './widgets/StockHeatmapWidget'
import TopStoriesWidget from './widgets/TopStoriesWidget'

const WATCHLIST = [
   'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'NFLX', 'DIS',
   'JPM', 'V', 'JNJ', 'PFE', 'WMT', 'KO', 'XOM', 'BA', 'COIN', 'INTC',
 ]
const watchlistSectors = JSON.stringify([
  { sectionName: 'Indices', symbols: ['FOREXCOM:SPXUSD', 'FOREXCOM:NSXUSD', 'FOREXCOM:DJI', 'FOREXCOM:UKXGBP'] },
  { sectionName: 'Stocks', symbols: WATCHLIST },
  { sectionName: 'Crypto', symbols: ['BITSTAMP:BTCUSD', 'BITSTAMP:ETHUSD', 'CRYPTO:XRPUSD'] },
])

function HomePage() {
  return (
    <div className="home-page">
      <h1>Stock Snap</h1>
      <p className="subtitle">Daily gainers, losers, volume spikes, and more across your watchlist</p>

      <div className="home-grid">
        <div className="home-widget">
          <h2>Market Overview</h2>
          <div style={{ height: 400, overflowY: 'auto' }}>
            <tv-market-overview symbol-sectors={watchlistSectors} theme="dark"></tv-market-overview>
          </div>
        </div>
        <div className="home-widget">
          <h2>S&amp;P 500 Heatmap</h2>
          <StockHeatmapWidget />
        </div>
        <div className="home-widget home-widget-tall">
          <h2>Economic Calendar</h2>
          <EconomicCalendarWidget />
        </div>

        <div className="home-widget">
          <h2>Top Stories</h2>
          <TopStoriesWidget />
        </div>
        <div className="home-widget">
          <h2>Watchlist Quotes</h2>
          <div style={{ height: 600, overflowY: 'auto' }}>
            <tv-market-data symbol-sectors={watchlistSectors} theme="dark"></tv-market-data>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
