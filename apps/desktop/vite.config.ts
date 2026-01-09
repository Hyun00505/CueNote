import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import { copyFileSync } from 'fs';

export default defineConfig({
  root: path.resolve(__dirname, 'renderer'),
  plugins: [
    vue(),
    {
      name: 'copy-preload',
      closeBundle() {
        // 빌드 후 preload.js를 dist 폴더로 복사
        const src = path.resolve(__dirname, 'renderer', 'preload.js');
        const dest = path.resolve(__dirname, 'dist', 'preload.js');
        try {
          copyFileSync(src, dest);
          console.log('✓ preload.js copied to dist/');
        } catch (e) {
          console.error('Failed to copy preload.js:', e);
        }
      }
    }
  ],
  server: {
    port: 5173
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'renderer', 'src')
    }
  },
  build: {
    outDir: path.resolve(__dirname, 'dist'),
    emptyOutDir: true
  }
});
