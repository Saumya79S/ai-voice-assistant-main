import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiProtocol = env.VITE_API_PROTOCOL || 'http'
  const apiHost = env.VITE_API_HOST || ''
  const apiPort = env.VITE_API_PORT || '8001'
  const viteHost = env.npm_config_host || ''
  const explicitApiTarget = env.VITE_API_TARGET || env.VITE_BACKEND_URL
  const fallbackHost = apiHost || viteHost || '127.0.0.1'
  const fallbackTarget = `${apiProtocol}://${fallbackHost}:${apiPort}`

  const resolveProxyTarget = (req) => {
    if (apiHost) return `${apiProtocol}://${apiHost}:${apiPort}`
    if (explicitApiTarget) return explicitApiTarget

    const forwardedHost = req.headers['x-forwarded-host']
    const headerHost = (Array.isArray(forwardedHost) ? forwardedHost[0] : forwardedHost) || req.headers.host || ''
    const hostOnly = String(headerHost).split(',')[0].trim().split(':')[0]
    if (!hostOnly) return fallbackTarget

    return `${apiProtocol}://${hostOnly}:${apiPort}`
  }

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          target: fallbackTarget,
          changeOrigin: true,
          router: resolveProxyTarget,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})
