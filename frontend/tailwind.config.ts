import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/app/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar: "#2d1b69",
        sidebarHover: "#3d2a7a",
        sidebarActive: "#4a3580",
        accent: "#6366f1",
        teal: "#2ac7c6",
      },
    },
  },
  plugins: [],
};
export default config;
