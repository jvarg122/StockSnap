import { useEffect, useRef, memo } from 'react'

function FundamentalDataWidget({ symbol }) {
  const container = useRef()

  useEffect(() => {
    const el = container.current
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-financials.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = `
      {
        "symbol": "${symbol}",
        "colorTheme": "dark",
        "displayMode": "regular",
        "isTransparent": true,
        "locale": "en",
        "width": 400,
        "height": 550
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
        <a href={`https://www.tradingview.com/symbols/${symbol}/financials-overview/`} rel="noopener nofollow" target="_blank">
          <span className="blue-text">{symbol} fundamentals</span>
        </a>
      </div>
    </div>
  )
}

export default memo(FundamentalDataWidget)
