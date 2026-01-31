/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",  // 모든 컴포넌트 스캔
    ],
    theme: {
        extend: {
            // 프로젝트 커스텀 디자인 토큰
            colors: {
                primary: {
                    50: '#eff6ff',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                },
                surface: {
                    DEFAULT: '#ffffff',
                    dark: '#1e1e1e',      // 다크모드 대비
                },
                warning: '#f59e0b',
                danger: '#ef4444',
            },
            fontFamily: {
                sans: ['Pretendard', 'sans-serif'],  // 한글 폰트
            },
            // 타임라인 전용 값
            spacing: {
                'timeline-gap': '2rem',
                'sidebar-width': '280px',
            },
            animation: {
                'fade-in': 'fadeIn 0.2s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'expand-in': 'expandIn 0.35s cubic-bezier(0.16,1,0.3,1)',
                'toast-in': 'toastIn 0.3s ease-out',
                'toast-out': 'toastOut 0.25s ease-in forwards',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                expandIn: {
                    '0%': { opacity: '0', transform: 'scale(0.97) translateX(20px)' },
                    '100%': { opacity: '1', transform: 'scale(1) translateX(0)' },
                },
                toastIn: {
                    '0%': { opacity: '0', transform: 'translateX(100%)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                toastOut: {
                    '0%': { opacity: '1', transform: 'translateX(0)' },
                    '100%': { opacity: '0', transform: 'translateX(100%)' },
                },
            },
        },
    },
    plugins: [],
}