# Kenny Gem Finder - Frontend

Next.js frontend for the Kenny Gem Finder application.

## Prerequisites

You need Node.js installed on your system.

### Install Node.js (macOS)

**Option 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Verify installation
node --version
npm --version
```

**Option 2: Download from nodejs.org**
1. Go to https://nodejs.org/
2. Download the LTS version
3. Run the installer
4. Verify: `node --version && npm --version`

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Axios (HTTP client)
- TanStack Query (React Query)

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local` if your backend is running on a different port:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The page will auto-update as you edit files.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page (search interface)
│   ├── providers.tsx      # React Query provider
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── SearchInterface.tsx    # Search input + examples
│   ├── ProductCard.tsx        # Product display card
│   ├── TierBadge.tsx          # Good/Better/Best badges
│   └── LoadingState.tsx       # Loading animation
├── lib/                   # Utilities
│   └── api.ts            # API client (Axios)
├── types/                # TypeScript types
│   └── index.ts          # API response types
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── tailwind.config.ts    # Tailwind CSS config
└── next.config.js        # Next.js config
```

## Features

### Search Interface
- Large textarea for natural language queries
- Example prompts for inspiration
- Loading state with progress indicators

### Product Display
- **Tier Badges**: Visual Good/Better/Best indicators
- **Value Metrics**: Prominent cost-per-year and cost-per-day
- **Key Features**: Bullet list of product highlights
- **Why It's a Gem**: AI-generated explanation
- **Trade-offs**: Honest drawbacks
- **Web Sources**: Links to Reddit and review sites

### Product Detail Modal
- Click any product card to see full details
- Expanded value breakdown
- All features and trade-offs
- Source citations
- Maintenance level

## Tier System

### 🟢 GOOD Tier
- **Price**: $20-80
- **Lifespan**: 2-5 years
- **Best For**: Students, renters, temporary living
- **Color**: Green (#10b981)

### 🔵 BETTER Tier
- **Price**: $80-200
- **Lifespan**: 8-15 years
- **Best For**: Homeowners, serious cooks
- **Color**: Blue (#3b82f6)

### 🟣 BEST Tier
- **Price**: $200-600+
- **Lifespan**: 15-30+ years
- **Best For**: Lifetime investment, heirloom quality
- **Color**: Purple (#8b5cf6)

## Building for Production

```bash
npm run build
npm start
```

The optimized build will be in `.next/` directory.

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import repository
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy!

Vercel automatically detects Next.js and configures everything.

### Other Platforms

Next.js can be deployed to:
- Netlify
- Railway
- AWS Amplify
- Any platform supporting Node.js

## Development Tips

### Hot Reload
Next.js has fast refresh - changes appear instantly without losing state.

### API Connection
The frontend connects to the backend at `http://localhost:8000` (configured in `.env.local`).

Make sure the backend is running:
```bash
cd ../backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Styling
Using Tailwind CSS utility classes. Main colors:
- `bg-tier-good` - Green for GOOD tier
- `bg-tier-better` - Blue for BETTER tier
- `bg-tier-best` - Purple for BEST tier

### Type Safety
TypeScript types in `types/index.ts` match the backend Pydantic models exactly.

## Troubleshooting

### "Cannot find module 'next'"
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or run on different port
npm run dev -- -p 3001
```

### Backend connection refused
- Check backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS is enabled in backend

### Styles not applying
```bash
# Restart dev server
npm run dev
```

## Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm start` - Run production build
- `npm run lint` - Run ESLint

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Font**: Inter (Google Fonts)

## Performance

- Fast Refresh for instant updates
- Automatic code splitting
- Image optimization (Next.js Image component)
- Server-side rendering ready
- Static generation for fast loads

## Future Enhancements

- [ ] Product comparison tool
- [ ] Save favorite products (localStorage)
- [ ] Filter by price range
- [ ] Sort by cost-per-year
- [ ] Share search results (URL params)
- [ ] Dark mode
- [ ] Mobile app (React Native)

---

**Frontend is ready to connect to the backend!** 🎨

Once Node.js is installed and dependencies are installed, run `npm run dev` and open http://localhost:3000
