import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import util from 'node:util'

// Polyfill util.styleText for Node 21.7 array formatting compatibility with Vite/Rolldown
if (typeof (util as any).styleText === 'function') {
  const orig = (util as any).styleText;
  (util as any).styleText = (format: any, text: any) => {
    if (Array.isArray(format)) {
      return format.reduce((acc: string, f: string) => orig(f, acc), text);
    }
    return orig(format, text);
  };
}

function resolveProxyTarget(env: Record<string, string>): string {
  // Explicit backend proxy target takes precedence
  if (env.VITE_OOPSIE_BACKEND_URL) {
    return env.VITE_OOPSIE_BACKEND_URL;
  }
  // If VITE_OOPSIE_API_URL is an absolute HTTP/HTTPS URL, extract the origin
  const apiUrl = env.VITE_OOPSIE_API_URL;
  if (apiUrl && /^https?:\/\//i.test(apiUrl)) {
    try {
      return new URL(apiUrl).origin;
    } catch {
      // Fallback to default
    }
  }
  return 'http://127.0.0.1:8000';
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        '/api': {
          target: resolveProxyTarget(env),
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  };
})
