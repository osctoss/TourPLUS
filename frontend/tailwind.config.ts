import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#103044",
        "primary-hover": "#0C2433",
        blue: {
          DEFAULT: "#1B74A8",
          dark: "#145982",
          light: "#E6F4FA",
        },
        green: {
          DEFAULT: "#259970",
          dark: "#1C7556",
          mint: "#E4F6EF",
        },
        cyan: {
          DEFAULT: "#2DA6C9",
          light: "#EAF6FA",
        },
        surface: "#F4F7F9",
        body: "#233038",
        muted: "#697781",
        border: "#D6E1E8",
        danger: "#B94A48",
        warning: "#A66B16",
      },
      fontFamily: {
        heading: ["Montserrat", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "14px",
      },
      boxShadow: {
        subtle: "0 2px 8px -2px rgba(16, 48, 68, 0.08)",
        card: "0 4px 16px -4px rgba(16, 48, 68, 0.06)",
      },
    },
  },
  plugins: [],
};

export default config;

