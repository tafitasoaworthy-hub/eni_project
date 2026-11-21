/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fbf3f3", 100: "#f6e3e3", 200: "#edc5c5", 300: "#e09d9d",
          400: "#cf6b6b", 500: "#b23a3a", 600: "#8b1a1a", 700: "#6d1414",
          800: "#5a1414", 900: "#4d1515",
        },
        gold: "#c9a227",
        ink: "#1d2330",
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(16,24,40,.06), 0 1px 2px rgba(16,24,40,.04)",
        soft: "0 4px 20px rgba(16,24,40,.08)",
      },
    },
  },
  plugins: [],
};
