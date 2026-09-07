import { useEffect, useRef, memo } from 'react'

function AdvancedChartWidget({ symbol }) {
  const container = useRef()

  useEffect(() => {
    const el = container.current
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = `
      {
        "allow_symbol_change": true,
        "calendar": false,
        "details": false,
        "hide_side_toolbar": true,
        "hide_top_toolbar": false,
        "hide_legend": false,
        "hide_volume": false,
        "hotlist": false,
        "interval": "D",
        "locale": "en",
        "save_image": true,
        "style": "1",
        "symbol": "${symbol}",
        "theme": "dark",
        "timezone": "Etc/UTC",
        "backgroundColor": "#ffffff",
        "gridColor": "rgba(46, 46, 46, 0.2)",
        "watchlist": [],
        "withdateranges": false,
        "compareSymbols": [],
        "support_host": "https://www.tradingview.com",
        "studies": [],
        "autosize": true
      }`
    el.appendChild(script)

    return () => {
      el.innerHTML = ''
    }
  }, [symbol])

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: '100%', width: '100%' }}>
      <div className="tradingview-widget-container__widget" style={{ height: 'calc(100% - 32px)', width: '100%' }}></div>
      <div className="tradingview-widget-copyright">
        <a href={`https://www.tradingview.com/symbols/${symbol}/`} rel="noopener nofollow" target="_blank">
          <span className="blue-text">{symbol} stock chart</span>
        </a>
      </div>
    </div>
  )
}

export default memo(AdvancedChartWidget)
