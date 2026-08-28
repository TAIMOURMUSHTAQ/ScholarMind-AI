/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#f2f6ff",
          100: "#e6edff",
          200: "#c2d3ff",
          300: "#9db8ff",
          400: "#5c85ff",
          500: "#3b63f5",
          600: "#2c49d6",
          700: "#2338ab",
          800: "#1c2c85",
          900: "#18265f",
        },
      },
    },
  },
  plugins: [],
};
