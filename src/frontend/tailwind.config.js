/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        cyber: {
          ink: '#050914',
          deep: '#081226',
          panel: '#0b1b3a',
          line: '#1b3766',
          cyan: '#5fd3f3',
          blue: '#3a6ed8',
          glow: '#4ea8ff',
          violet: '#7c5cff',
          magenta: '#ff4fd8',
          lime: '#8bffb0',
          amber: '#ffcc66',
          red: '#ff5f7e',
        },
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'Silkscreen', 'monospace'],
        mono: ['VT323', '"Cascadia Code"', 'Consolas', 'monospace'],
        body: ['"Noto Sans SC"', '"Microsoft YaHei"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        pixel: '0 6px 0 #03060d, 0 14px 34px rgba(0, 0, 0, 0.45)',
        'pixel-sm': '0 4px 0 #03060d, 0 8px 20px rgba(0, 0, 0, 0.35)',
        glow: '0 0 24px rgba(95, 211, 243, 0.28)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-14px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-120%)' },
          '100%': { transform: 'translateY(120vh)' },
        },
        blink: {
          '0%, 49%': { opacity: '1' },
          '50%, 100%': { opacity: '0' },
        },
      },
      animation: {
        float: 'float 5s ease-in-out infinite',
        'float-slow': 'float 7s ease-in-out infinite',
        scan: 'scan 9s linear infinite',
        blink: 'blink 1.1s steps(1) infinite',
      },
    },
  },
  plugins: [],
}
