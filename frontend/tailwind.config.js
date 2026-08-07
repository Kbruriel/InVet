/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: "#006065",
          light: "#008085",
          dark: "#00484c",
        },
        mint: "#bcedda",
        sandy: {
          100: "#fff8f0",
          200: "#faf3e8",
          300: "#f4ede2",
        },
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
