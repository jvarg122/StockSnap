import { useEffect, useRef, memo } from 'react'

function TopStoriesWidget() {
  const container = useRef()

  useEffect(() => {
    const el = container.current
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-timeline.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = `
      {
        "displayMode": "regular",
        "feedMode": "all_symbols",
        "colorTheme": "dark",
        "isTransparent": true,
        "locale": "en",
        "width": "100%",
        "height": 500
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
        <a href="https://www.tradingview.com/news/top-providers/tradingview/" rel="noopener nofollow" target="_blank">
          <span className="blue-text">Top stories</span>
        </a>
      </div>
    </div>
  )
}

export default memo(TopStoriesWidget)
