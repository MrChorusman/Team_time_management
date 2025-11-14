import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js',
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
    extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json']
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // PASO 1: Reactivar minificación con configuración ULTRA-CONSERVADORA
    // Solo minificar sintaxis y espacios, NO renombrar identificadores
    // Esto reduce el tamaño sin tocar nombres de variables/funciones
    minify: 'esbuild',
    esbuild: {
      // CRÍTICO: NO renombrar identificadores - esto causaba el error original
      minifyIdentifiers: false,
      // Minificar solo sintaxis (eliminar código muerto, optimizar expresiones)
      minifySyntax: true,
      // Minificar solo espacios en blanco (reducir tamaño sin cambiar lógica)
      minifyWhitespace: true,
      // Preservar nombres de funciones para debugging
      keepNames: true,
      // Mantener comentarios legales para debugging
      legalComments: 'inline'
    },
    // PASO 2: Activar manualChunks de forma ULTRA-CONSERVADORA
    // Solo separar React y vendor básico, sin tocar componentes del calendario todavía
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Solo separar React y React-DOM (lo más crítico)
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor'
            }
            // Todo lo demás va a vendor (sin más separaciones por ahora)
            return 'vendor'
          }
          // NO separar componentes del calendario todavía - dejarlos en el bundle principal
          // Esto evita problemas de inicialización mientras probamos la minificación básica
        }
      }
    }
  },
  preview: {
    port: 3000,
    host: true
  }
})
