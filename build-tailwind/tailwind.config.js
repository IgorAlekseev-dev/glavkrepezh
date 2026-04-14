/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../templates/**/*.html",
    "../src/**/*.py",
  ],

  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#1e293b',
          primary: '#2563eb',
          accent: '#f97316',
          accentHover: '#ea580c',
          light: '#f8fafc',
          surface: '#ffffff',
        }
      },

      fontFamily: {
        sans: ['"Exo 2"', 'sans-serif'],
        display: ['"Exo 2"', 'sans-serif'],
      },

      boxShadow: {
        card: '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03)',
        hover: '0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)',
      },

      container: {
        center: true,
        padding: '1rem',
        screens: {
          sm: '640px',
          md: '768px',
          lg: '1024px',
          xl: '1280px',
        },
      },
    },
  },

  plugins: [],
}