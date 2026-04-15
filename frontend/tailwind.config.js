/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        verde: {
          50:  '#f0f7f0',
          100: '#dceddc',
          200: '#b8dab8',
          300: '#8cc28c',
          400: '#5ca65c',
          500: '#2E7D32',
          600: '#1B5E20',
          700: '#164d1a',
          800: '#103d14',
          900: '#0a2d0e',
        },
        amarillo: {
          400: '#F9A825',
          500: '#F57F17',
        }
      },
      fontFamily: {
        sans:    ['DM Sans', 'sans-serif'],
        display: ['Playfair Display', 'serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.12), 0 8px 32px rgba(0,0,0,0.08)',
      }
    },
  },
  plugins: [],
}