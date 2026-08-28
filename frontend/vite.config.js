import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // backend runs on 8000 during dev, this avoids CORS setup for now
      '/api': 'http://localhost:8000',
    },
  },
})
