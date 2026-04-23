/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#FF6B9D", 500: "#FF6B9D", 600: "#FF3D7F", foreground: "#FFFFFF" },
        secondary: { DEFAULT: "#5E17EB", 500: "#5E17EB", 600: "#4B12BC", foreground: "#FFFFFF" },
        accent: { DEFAULT: "#00D9FF", foreground: "#000000" },
        success: { DEFAULT: "#10B981", foreground: "#FFFFFF" },
        warning: { DEFAULT: "#F59E0B", foreground: "#000000" },
        destructive: { DEFAULT: "#EF4444", foreground: "#FFFFFF" },
      },
      borderRadius: { lg: "0.5rem", md: "0.375rem", sm: "0.25rem" },
      animation: { "fade-in": "fadeIn 0.5s ease-out", "slide-up": "slideUp 0.5s ease-out" },
      keyframes: {
        fadeIn: { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { opacity: "0", transform: "translateY(20px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
}
