module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FFD600', // أصفر الشعار
          dark: '#FFC400',
          light: '#FFF9C4',
        },
        secondary: {
          DEFAULT: '#7C3AED', // بنفسجي الشعار
          dark: '#5B21B6',
          light: '#EDE9FE',
        },
      },
    },
  },
  plugins: [],
} 