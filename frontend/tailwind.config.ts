import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'tier-good': '#10b981',
        'tier-better': '#3b82f6',
        'tier-best': '#8b5cf6',
      },
    },
  },
  plugins: [],
}
export default config
