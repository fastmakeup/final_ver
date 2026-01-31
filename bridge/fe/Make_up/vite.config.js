import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // ★ exe 패키징 핵심: 상대 경로로 빌드
  // pywebview가 file:// 프로토콜로 로드하므로 절대경로('/')면 깨짐
  base: './',

  // @ 경로 별칭 → import { cn } from '@/shared/utils/cn'
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  build: {
    // dist 폴더에 빌드 결과물 생성
    outDir: 'dist',
    // 소스맵은 배포 시 불필요 (exe 용량 줄이기)
    sourcemap: false,
    // 청크 경고 임계값 (KB)
    chunkSizeWarningLimit: 1000,
  },

  server: {
    // 개발 서버 포트 (pywebview 개발 모드에서 이 주소를 로드)
    port: 5173,
    // 자동 브라우저 열기 방지 (pywebview가 대신 열어줌)
    open: false,
  },
})
