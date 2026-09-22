/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e8eaf6', 100: '#c5cae9', 500: '#3f51b5', 600: '#3949ab', 700: '#303f9f', 900: '#1a237e',
        },
        severity: {
          critical: '#dc2626', high: '#ea580c', medium: '#ca8a04', low: '#16a34a', info: '#0891b2',
        }
      },
    },
  },
  plugins: [],
}
