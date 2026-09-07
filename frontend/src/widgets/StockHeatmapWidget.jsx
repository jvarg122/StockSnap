import { useEffect, useRef, memo } from 'react'

function StockHeatmapWidget() {
  const container = useRef()

  useEffect(() => {
    const el = container.current
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = `
      {
        "dataSource": "SPX500",
        "blockSize": "market_cap_basic",
        "blockColor": "change",
        "grouping": "sector",
        "locale": "en",
        "symbolUrl": "",
        "colorTheme": "dark",
        "exchanges": [],
        "hasTopBar": false,
        "isDataSetEnabled": false,
        "isZoomEnabled": true,
        "hasSymbolTooltip": true,
        "isMonoSize": false,
        "width": "100%",
        "height": "92%"
      }`
    el.appendChild(script)

    return () => {
      el.innerHTML = ''
    }
  }, [])

  return (
    <div className="tradingview-widget-container" ref={container}>
      <div className="tradingview-widget-container__widget"></div>
      <div className="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/heatmap/stock/" rel="noopener nofollow" target="_blank">
          <span className="blue-text">Stock Heatmap</span>
        </a>
      </div>
    </div>
  )
}

export default memo(StockHeatmapWidget)
