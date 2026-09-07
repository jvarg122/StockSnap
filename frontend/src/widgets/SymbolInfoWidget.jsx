import { useEffect, useRef, memo } from 'react'

function SymbolInfoWidget({ symbol }) {
  const container = useRef()

  useEffect(() => {
    const el = container.current
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = `
      {
        "symbol": "${symbol}",
        "colorTheme": "dark",
        "isTransparent": true,
        "locale": "en",
        "width": "550"
      }`
    el.appendChild(script)

    return () => {
      el.innerHTML = ''
    }
  }, [symbol])

  return (
    <div className="tradingview-widget-container" ref={container}>
      <div className="tradingview-widget-container__widget"></div>
      <div className="tradingview-widget-copyright">
        <a href={`https://www.tradingview.com/symbols/${symbol}/`} rel="noopener nofollow" target="_blank">
          <span className="blue-text">{symbol} performance</span>
        </a>
      </div>
    </div>
  )
}

export default memo(SymbolInfoWidget)
