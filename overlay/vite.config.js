import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  server: {
    port: 3000,
    open: true,
    strictPort: true, // Ensures the server fails if the port is already in use
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Simplify imports with alias
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // Generate source maps for easier debugging
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['socket.io-client', 'chart.js'], // Separate vendor libraries for better caching
        },
      },
    },
  },
});
